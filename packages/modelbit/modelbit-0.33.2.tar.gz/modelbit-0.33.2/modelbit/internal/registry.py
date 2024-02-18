import base64
import codecs
from datetime import datetime, timedelta
import json
import logging, pickle
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union, TextIO
from tqdm import tqdm
from io import StringIO

from modelbit.api import MbApi, BranchApi, RegistryApi
from modelbit.error import UserFacingError
from modelbit.helpers import getCurrentBranch
from modelbit.internal.auth import isAuthenticated as isAuthenticated
from modelbit.internal.describe import calcHash, describeObject
from modelbit.internal.retry import retry
from modelbit.internal.runtime_objects import downloadRuntimeObject, uploadRuntimeObject
from modelbit.internal.s3 import getS3FileBytes
from modelbit.internal.secure_storage import DownloadableObjectInfo, getSecureData
from modelbit.utils import boto3Client, inDeployment, inRuntimeJob, maybePlural, tryPickle
from modelbit.ux import printTemplate
from modelbit.keras_wrapper import KerasWrapper
import zstandard
from Cryptodome.Cipher import AES

from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad

logger = logging.getLogger(__name__)

_reg_cache: Optional[Tuple[datetime, str]] = None
_obj_cache: Dict[str, Any] = {}

_usedModelsByFunction: Dict[str, List[Any]] = {}  # function name to list of models


def registryCacheTtl():
  if inDeployment():
    return timedelta(seconds=60)
  return timedelta(seconds=10)


def set(api: MbApi, name: str, model: Any, metrics: Optional[Dict[str, Any]] = None):
  BranchApi(api).raiseIfProtected()
  _assertSetModelFormat(name, model, metrics)
  set_many(api, {name: model}, {name: metrics})


def set_many(api: MbApi,
             models: Dict[str, Any],
             metrics: Optional[Dict[str, Optional[Dict[str, Any]]]] = None):
  BranchApi(api).raiseIfProtected()
  _assertSetModelsFormat(models, metrics)

  _storeJobModels(models, metrics) if inRuntimeJob() else _uploadModelFromNotebook(api, models, metrics)
  printTemplate(
      "message",
      None,
      msgText=f"Success: {len(models)} {maybePlural(len(models), 'model')} added to the registry.",
  )


def _storeJobModels(models: Dict[str, Any], metrics: Optional[Dict[str, Any]]):
  modelMetadata: Dict[str, Any] = {}

  for name, obj in models.items():
    objData = tryPickle(_maybeWrap(obj), name)

    contentHash = calcHash(objData)
    description = describeObject(obj, 1)
    size = len(objData)

    _encryptAndUploadToS3(_jobS3Key(f"runtime_objects/{contentHash}"), objData)
    modelMetadata[name] = {
        "contentHash": contentHash,
        "metadata": {
            "size": size,
            "description": description,
            "trainingJobId": os.environ.get("JOB_ID", None),
            "metrics": metrics.get(name) if metrics else None
        },
    }

  _assertSetModelsRequestSize(modelMetadata)
  _encryptAndUploadToS3(_jobS3Key(f"registry/{datetime.now().isoformat()}"),
                        json.dumps(modelMetadata).encode())


def _encryptAndUploadToS3(s3Key: str, data: bytes):
  _workspaceId = os.getenv('WORKSPACE_ID', "")
  _pystateBucket = os.getenv('PYSTATE_BUCKET', "")
  _pystateKeys = os.getenv('PYSTATE_KEYS', "")
  if not _workspaceId or not _pystateBucket or not _pystateKeys:
    raise Exception(f"EnvVar Missing: WORKSPACE_ID, PYSTATE_BUCKET, PYSTATE_KEYS")

  iv = get_random_bytes(16)
  key = get_random_bytes(32)
  cipher = AES.new(  # type: ignore
      mode=AES.MODE_CBC, key=key, iv=iv)
  fileKeyCipher = AES.new(  # type: ignore
      mode=AES.MODE_ECB, key=base64.b64decode(_pystateKeys.split(",")[0]))
  encFileKey = fileKeyCipher.encrypt(pad(key, AES.block_size))
  body = cipher.encrypt(pad(zstandard.compress(data, 10), AES.block_size))

  try:
    boto3Client("s3").put_object(  #type: ignore
        Bucket=_pystateBucket,
        Key=f"{_workspaceId}/{s3Key}.zstd.enc",
        Metadata={
            "x-amz-key": base64.b64encode(encFileKey).decode(),
            "x-amz-iv": base64.b64encode(iv).decode()
        },
        Body=body)
  except:
    pass


def _jobS3Key(suffix: str):
  _runtimeName = os.getenv("DEPLOYMENT_NAME", "")
  _jobName = os.getenv("JOB_NAME", "")
  _jobId = os.getenv("JOB_ID", "")

  if not _runtimeName or not _jobName or not _jobId:
    raise Exception(f"EnvVar Missing: DEPLOYMENT_NAME, JOB_NAME, JOB_ID")

  return "/".join(["jobs", _runtimeName, _jobName, _jobId, suffix])


def _uploadModelFromNotebook(api: MbApi,
                             models: Dict[str, Any],
                             metrics: Optional[Dict[str, Any]],
                             batchSize: int = 100):
  perFileLoader = len(models) < 10
  uploadedObjects: Dict[str, Any] = {}
  uploadedObjectBatches = [uploadedObjects]
  outputStream: TextIO = StringIO() if os.getenv('MB_TXT_MODE') else sys.stdout
  readyMetrics: Dict[str, Any] = metrics if metrics else {}

  if perFileLoader:
    for name, obj in models.items():
      uploadedObjects[name] = _pickleAndUpload(api, name, obj, True, readyMetrics.get(name))
  else:
    for name, obj in tqdm(models.items(),
                          desc=f"Uploading {len(models)} models",
                          bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} models [{elapsed}<{remaining}]",
                          file=outputStream):
      if (len(uploadedObjects) >= batchSize):
        uploadedObjects = {}
        uploadedObjectBatches.append(uploadedObjects)
      uploadedObjects[name] = _pickleAndUpload(api, name, obj, False, readyMetrics.get(name))

  for uploadedObjects in tqdm(uploadedObjectBatches,
                              desc=f"Updating registry",
                              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                              file=outputStream):
    _assertSetModelsRequestSize(uploadedObjects)
    RegistryApi(api).storeContentHashAndMetadata(uploadedObjects)


def get(api: MbApi, name: str):
  _assertGetFormat(name)

  if (inDeployment() and name in _obj_cache):
    obj = _obj_cache[name]
    _logModelUsed(name, obj)
    return obj

  reg = _getRegistry(api)
  assert reg is not None

  for line in reg.split("\n"):
    if line.startswith(f"{name}="):
      jsonStr = line[len(name) + 1:]
      hash = _tryReadHash(jsonStr)
      if hash:
        obj = _getObject(api, name, hash)
        _logModelUsed(name, obj)
        return obj
  raise UserFacingError(f"Model not found: {name}")


def getMetrics(api: MbApi, nameOrNames: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
  if type(nameOrNames) is str:
    metrics = RegistryApi(api).fetchModelMetrics([nameOrNames])
    return metrics.get(nameOrNames, None)
  elif type(nameOrNames) is list:
    for n in nameOrNames:
      if type(n) is not str:
        raise UserFacingError(f"Model names must be strings. Found {n} which is a {type(n)}.")
      if n == "":
        raise UserFacingError(f"Model names cannot be empty strings.")
    if len(nameOrNames) == 0:
      raise UserFacingError(f"Supply at least one model name to fetch metrics.")
    return RegistryApi(api).fetchModelMetrics(nameOrNames)
  else:
    raise UserFacingError(f"Error getting metrics. Expecting str or List[str] but found {type(nameOrNames)}")


def _logModelUsed(name: str, model: Any):
  if inDeployment():
    print(f'![mb:model]({name})')  # for parsing out of stdout later
  else:
    import traceback
    foundGetModel = False
    frame = traceback.extract_stack()
    frame.reverse()
    for f in frame:
      if not foundGetModel:  # first, look for get_model in stack
        if f.name == "get_model":
          foundGetModel = True
        continue
      if f.filename.endswith("modelbit/telemetry.py"):  # then skip over internal wrappers
        continue
      if f.name not in _usedModelsByFunction:  # finally, capture name of function that called get_model
        _usedModelsByFunction[f.name] = []
      if model not in _usedModelsByFunction[f.name]:
        _usedModelsByFunction[f.name].append(model)
      return


def recentlyUsedModels(funcName: str) -> List[Any]:
  return _usedModelsByFunction.get(funcName, []).copy()


def resetRecentlyUsedModels():
  _usedModelsByFunction.clear()


def list_names(api: MbApi, prefix: Optional[str] = None):
  _assertListFormat(prefix)

  reg = _getRegistry(api)
  assert reg is not None

  if prefix is not None:
    return [line[0:line.index("=")] for line in reg.split("\n") if line.startswith(prefix)]
  else:
    return [line[0:line.index("=")] for line in reg.split("\n")]


def delete(api: MbApi, names: Union[str, List[str]]):
  BranchApi(api).raiseIfProtected()
  _assertDeleteFormat(names)
  if not isinstance(names, List):
    names = [names]

  RegistryApi(api).delete(names)
  printTemplate(
      "message",
      None,
      msgText=f"Success: {len(names)} {maybePlural(len(names), 'model')} removed from the registry.",
  )


def _assertSetModelFormat(name: str, model: Any, metrics: Optional[Dict[str, Any]]):
  if type(name) is not str:
    raise UserFacingError(f"name= must be a string. It's currently a {type(name)}")
  if not name:
    raise UserFacingError(f"name= must not be empty.")
  if len(name) < 2:
    raise UserFacingError(f"Model names must be at least two characters.")
  if model is None:
    raise UserFacingError(f"model= must not be None.")
  _assertSetModelMetricsFormat({name: metrics}, [name])


def _assertSetModelsFormat(models: Dict[str, Any], metrics: Optional[Dict[str, Any]]):
  if type(models) is not dict:
    raise UserFacingError(f"models= must be a dictionary. It's currently a {type(models)}")
  if len(models) == 0:
    raise UserFacingError(f"The dict of models to add cannot be empty.")
  for k, v in models.items():
    if type(k) is not str:
      raise UserFacingError(f"Model keys must be strings. Found '{k}' which is a {type(v)}")
    if not k:
      raise UserFacingError(f"Model keys must not be empty.")
    if v is None:
      raise UserFacingError(f"Model values must not be None.")
    if len(k) < 2:
      raise UserFacingError(f"Model keys must be at least two characters.")
  _assertSetModelMetricsFormat(metrics, list(models.keys()))


def _assertSetModelMetricsFormat(metrics: Optional[Dict[str, Optional[Dict[str, Any]]]],
                                 modelNames: List[str]):
  if metrics is None:
    return
  if type(metrics) is not dict:
    raise UserFacingError(f"Model metrics must be a dictionary of modelName -> metricsDict.")

  for modelName, metricsDict in metrics.items():
    if type(modelName) is not str:
      raise UserFacingError(f"Expecting a string model name as the key, but found {type(modelName)}")
    if metricsDict is None:
      continue
    if type(metricsDict) is not dict:
      raise UserFacingError(f"Expecting a dictionary for metric values, but found {type(metricsDict)}")
    if modelName not in modelNames:
      raise UserFacingError(
          f"Model metrics must be a dictionary of modelName -> metricsDict. There is no model named '{modelName}' in this update."
      )

    for k, v in metricsDict.items():
      if type(k) is not str:
        raise UserFacingError(f"Metric keys must be strings. Found '{k}' which is a {type(k)}")
      if len(k) == 0:
        raise UserFacingError(f"Metric keys cannot be empty strings")
      try:
        json.dumps(v)
      except Exception as err:
        raise UserFacingError(
            f"Metric values must be JSON-serializable. The value of '{k}' is {type(v)}. Error: {err}")


def _assertSetModelsRequestSize(request: Dict[str, Any]):
  if len(json.dumps(request)) > 5_000_000:
    raise UserFacingError("Request size exceeds maximum allowed (5MB). Add fewer models at a time.")


def _assertDeleteFormat(names: Union[str, List[str]]):
  if type(names) is str:
    if not names:
      raise UserFacingError(f"names= must not be empty.")
    return
  if type(names) is list:
    if not names:
      raise UserFacingError(f"names= must not be empty.")
    for n in names:
      if type(n) is not str:
        raise UserFacingError(f"Names must only contain strings. Found '{n}' which is a {type(n)}")
      if not n:
        raise UserFacingError(f"Names must not contain empty strings")
    return
  raise UserFacingError(f"names= must be a string or a list of strings. It's currently a {type(names)}")


def _assertGetFormat(name: str):
  if type(name) is not str:
    raise UserFacingError(f"name= must be a string. It's currently a {type(name)}")
  if not name:
    raise UserFacingError(f"name= must not be empty.")


def _assertListFormat(prefix: Optional[str]):
  if prefix is None:
    return
  if type(prefix) is not str:
    raise UserFacingError(f"prefix= must be a string. It's currently a {type(prefix)}")
  if not prefix:
    raise UserFacingError(f"prefix= must not be empty.")


def _pickleAndUpload(api: MbApi, name: str, obj: Any, showLoader: bool, metrics: Optional[Dict[str, Any]]):
  objData = tryPickle(_maybeWrap(obj), name)

  contentHash = calcHash(objData)
  description = describeObject(obj, 1)
  size = len(objData)
  uploadRuntimeObject(api, objData, contentHash, name, showLoader)
  return {
      "contentHash": contentHash,
      "metadata": {
          "size": size,
          "description": description,
          "metrics": metrics
      },
  }


def _getRegistry(api: MbApi):
  global _reg_cache
  if _reg_cache:
    ts, reg = _reg_cache
    if datetime.now() - ts < registryCacheTtl():
      return reg
    else:
      _reg_cache = None

  reg = _getRegistryInDeployment() if inDeployment() else _getRegistryInNotebook(api)
  if reg:
    _reg_cache = datetime.now(), reg
  return reg


def _getRegistryInDeployment():
  registryBytes = _getS3RegistryBytes()
  if registryBytes:
    reg = registryBytes.decode("utf-8")
    return reg


def _getS3RegistryBytes():
  regPath = f"registry_by_branch/{getCurrentBranch()}/registry.txt.zstd.enc"
  return _wrappedGetS3FileBytes(regPath)


def _getRegistryInNotebook(api: MbApi):
  dri = RegistryApi(api).getRegistryDownloadInfo()
  if dri:
    return codecs.decode(_wrappedGetSecureData(dri, "model registry"))


def _tryReadHash(jsonStr: str):
  try:
    jRes = json.loads(jsonStr)
    hash = jRes.get("id", None)
    if type(hash) is str:
      return hash
  except json.JSONDecodeError:
    raise UserFacingError("Unable to find model in registry.")


def _getObject(api: MbApi, name: str, contentHash: str):
  if contentHash in _obj_cache:
    return _obj_cache[contentHash]

  obj = _getObjectInDeployment(name, contentHash) if inDeployment() else _getObjectInNotebook(
      api, name, contentHash)
  _obj_cache[contentHash] = obj
  return obj


def _getObjectInDeployment(name: str, contentHash: str):
  runtimeObjBytes = _getS3ObjectBytes(contentHash)
  assert runtimeObjBytes is not None
  try:
    return _maybeUnwrap(pickle.loads(runtimeObjBytes))
  except ModuleNotFoundError as err:
    raise UserFacingError(f"Module missing from environment: {str(err.name)}")
  except Exception as err:
    raise UserFacingError(f"{err.__class__.__name__} while loading model {name}: {err}")


def _getS3ObjectBytes(contentHash: str):
  return _wrappedGetS3FileBytes(f"runtime_objects/{contentHash}.zstd.enc")


def _getObjectInNotebook(api: MbApi, name: str, contentHash: str):
  try:
    return _maybeUnwrap(pickle.loads(downloadRuntimeObject(api, contentHash, name)))
  except ModuleNotFoundError as err:
    raise UserFacingError(f"Module missing from environment: {str(err.name)}")
  except Exception as err:
    raise UserFacingError(f"{err.__class__.__name__} while loading model {name}: {err}")


def _maybeWrap(model: Any):
  if KerasWrapper.isKerasModel(model):
    return KerasWrapper(model)
  return model


def _maybeUnwrap(obj: Any):
  if isinstance(obj, KerasWrapper):
    return obj.getModel()
  return obj


@retry(4, logger)
def _wrappedGetS3FileBytes(path: str):
  return getS3FileBytes(path)


@retry(4, logger)
def _wrappedGetSecureData(dri: DownloadableObjectInfo, desc: str):
  return getSecureData(dri, desc)
