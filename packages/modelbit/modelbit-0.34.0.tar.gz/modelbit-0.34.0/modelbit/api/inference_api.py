from typing import Optional, Any, Union, Dict, cast, List, TextIO
from modelbit.error import UserFacingError
from modelbit.utils import toUrlBranch, dumpJson
import re, requests
from requests import ConnectionError
import logging
import pandas, os, sys
from tqdm import tqdm
from io import StringIO

DefaultBatchSize = 10_000


def _isMissingArg(value: Any) -> bool:
  return value is None or value == ""


def _isInvalidUrlArg(value: Any) -> bool:
  return type(value) is not str or re.fullmatch("[a-zA-Z0-9./_:+=-]+", value) is None


def _assertValid(value: Any, param: str, bonusMessage: Optional[str] = None):
  if _isMissingArg(value):
    raise UserFacingError(f"Missing '{param}' value. {bonusMessage or ''}".strip())
  elif _isInvalidUrlArg(value):
    raise UserFacingError(f"Invalid '{param}' value (Received '{value}'). {bonusMessage or ''}".strip())


def _headers(apiKey: Optional[str]) -> Dict[str, str]:
  base: Dict[str, str] = {"Content-Type": "application/json"}
  if apiKey is not None:
    base["Authorization"] = apiKey
  return base


def inChunks(lst: List[Any], n: int):
  return [lst[i:i + n] for i in range(0, len(lst), n)]


def callDeployment(region: str,
                   workspace: Optional[str],
                   branch: Optional[str],
                   deployment: str,
                   version: Union[str, int],
                   data: Any,
                   apiKey: Optional[str],
                   timeoutSeconds: Optional[int],
                   batchChunkSize: Optional[int] = DefaultBatchSize) -> Dict[str, Any]:

  _assertValid(region, "region")
  _assertValid(workspace, "workspace", "Supply the 'workspace' parameter or set the MB_WORKSPACE_NAME envvar")
  _assertValid(branch, "branch")
  branch = cast(str, branch)
  _assertValid(deployment, "deployment")

  if _isMissingArg(version):
    raise UserFacingError(f"Missing 'version' value.")
  strVersion = str(version)
  _assertValid(strVersion, "version")

  if apiKey is not None:
    if type(apiKey) is not str:
      raise UserFacingError(f"Invalid API Key value.")
    _assertValid(apiKey, "api_key", "Supply the 'api_key' parameter or set the MB_API_KEY envvar")

  if timeoutSeconds is not None and (type(timeoutSeconds) is not int or timeoutSeconds <= 0):
    raise UserFacingError(f"Invalid 'timeout_seconds' value. It must be a positive integer.")

  if batchChunkSize is None:
    batchChunkSize = DefaultBatchSize
  elif type(batchChunkSize) is not int or batchChunkSize <= 0:
    raise UserFacingError(f"Invalid 'batch_size' value. It must be a positive integer.")

  url = f"https://{workspace}.{region}.modelbit.com/v1/{deployment}/{toUrlBranch(branch)}/{strVersion}"
  mbTimeoutParam = {"timeout_seconds": timeoutSeconds} if timeoutSeconds else {}
  rqTimeout = timeoutSeconds + 5 if timeoutSeconds else None
  convertedData = convertData(data)
  outputStream: TextIO = StringIO() if os.getenv('MB_TXT_MODE') else sys.stdout

  if canChunk(data, batchChunkSize):
    allResults: List[Any] = []
    for dataChunk in tqdm(inChunks(convertedData, batchChunkSize),
                          desc=f"Getting inferences",
                          bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} batches [{elapsed}<{remaining}]",
                          file=outputStream):

      chunkResults = makeRequest(url=url,
                                 headers=_headers(apiKey),
                                 data=dataChunk,
                                 extraParams=mbTimeoutParam,
                                 rqTimeout=rqTimeout)
      allResults += chunkResults["data"]
    return {"data": allResults}
  else:
    return makeRequest(url=url,
                       headers=_headers(apiKey),
                       data=convertedData,
                       extraParams=mbTimeoutParam,
                       rqTimeout=rqTimeout)


def canChunk(data: Any, batchSize: int) -> bool:
  if type(data) is pandas.DataFrame and len(data) > batchSize:
    return True
  if type(data) is list:
    data = cast(List[Any], data)
    if len(data) > 0 and type(data[0]) is list and len(data) > batchSize:
      return True
  return False


def makeRequest(url: str, headers: Dict[str, str], data: List[Any], extraParams: Dict[str, Any],
                rqTimeout: Optional[int]) -> Dict[str, Any]:
  try:
    result = requests.post(url,
                           headers=headers,
                           data=dumpJson({
                               "data": data,
                               **extraParams,
                           }),
                           timeout=rqTimeout).json()
    if "error" in result:
      print(result["error"], file=sys.stderr)
      raise UserFacingError(result["error"].split("\n")[-1])
    return result
  except ConnectionError as err:
    logging.error(err)
    raise UserFacingError(f"Unable to connect to '{url}'.")


def convertData(data: Any) -> Any:
  if type(data) is pandas.DataFrame:
    splitDict = data.to_dict(  # type: ignore
        orient="split")  # see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html
    records: List[Any] = []
    for rowIdx, dfIndex in enumerate(splitDict["index"]):
      dataRow: Dict[str, Any] = {}
      for cIdx, colName in enumerate(splitDict["columns"]):
        dataRow[colName] = splitDict["data"][rowIdx][cIdx]
      records.append([dfIndex, dataRow])
    return records
  return data
