from typing import Any, List, Optional, TYPE_CHECKING, Union, Dict

from modelbit.api import MbApi
from modelbit.runtime import Deployment
from modelbit.utils import getFuncName, convertLambdaToDef, tempPath

if TYPE_CHECKING:
  import pandas
  import modelbit.jobs as m_jobs


class LambdaWrapper:

  def __init__(self,
               lambdaFunc: Any,
               name: Optional[str] = None,
               python_version: Optional[str] = None,
               python_packages: Optional[List[str]] = None,
               system_packages: Optional[List[str]] = None,
               dataframe_mode: bool = False,
               example_dataframe: Optional['pandas.DataFrame'] = None,
               common_files: Union[List[str], Dict[str, str], None] = None,
               extra_files: Union[List[str], Dict[str, str], None] = None,
               skip_extra_files_dependencies: bool = False,
               snowflake_max_rows: Optional[int] = None,
               rate_limit_name: Optional[str] = None,
               require_gpu: Union[bool, str] = False):

    self.lambdaFunc = lambdaFunc
    self.python_version = python_version
    self.python_packages = python_packages
    self.system_packages = system_packages
    self.dataframe_mode = dataframe_mode
    self.example_dataframe = example_dataframe
    self.common_files = common_files
    self.extra_files = extra_files
    self.skip_extra_files_dependencies = skip_extra_files_dependencies
    self.snowflake_max_rows = snowflake_max_rows
    self.rate_limit_name = rate_limit_name
    self.require_gpu = require_gpu
    self.name = name if name is not None else getFuncName(self.lambdaFunc, "predict")

  def makeDeployment(self, api: MbApi):
    deployFunction, funcSource = convertLambdaToDef(self.lambdaFunc, self.name)

    return Deployment(api=api,
                      deploy_function=deployFunction,
                      source_override=funcSource,
                      python_version=self.python_version,
                      python_packages=self.python_packages,
                      system_packages=self.system_packages,
                      name=self.name,
                      dataframe_mode=self.dataframe_mode,
                      example_dataframe=self.example_dataframe,
                      common_files=self.common_files,
                      extra_files=self.extra_files,
                      skip_extra_files_dependencies=self.skip_extra_files_dependencies,
                      snowflake_max_rows=self.snowflake_max_rows,
                      rate_limit_name=self.rate_limit_name,
                      require_gpu=self.require_gpu)


class RuntimeJobWrapper:

  def __init__(
      self,
      job: 'm_jobs.ModelbitJobWrapper',
      name: str,
      python_version: Optional[str] = None,
      python_packages: Optional[List[str]] = None,
      system_packages: Optional[List[str]] = None,
      extra_files: Union[str, List[str], Dict[str, str], None] = None,
      skip_extra_files_dependencies: bool = False,
  ):
    self.job = job
    self.python_version = python_version
    self.python_packages = python_packages
    self.system_packages = system_packages
    self.extra_files = extra_files
    self.skip_extra_files_dependencies = skip_extra_files_dependencies
    self.name = name

  def makeDeployment(self, api: MbApi):
    return Deployment(api=api,
                      deploy_function=None,
                      job=self.job,
                      python_version=self.python_version,
                      python_packages=self.python_packages,
                      system_packages=self.system_packages,
                      name=self.name,
                      extra_files=self.extra_files,
                      skip_extra_files_dependencies=self.skip_extra_files_dependencies)


def start_sparknlp(gpu: bool = False,
                   apple_silicon: bool = False,
                   aarch64: bool = False,
                   memory: str = "5G") -> Any:
  import sparknlp  # type: ignore
  # Additional options: https://spark.apache.org/docs/latest/configuration.html
  SPARKNLP_PARAMS = {
      "spark.driver.host": "localhost",
      "spark.jars.ivy": tempPath("ivy"),
      "spark.driver.memory": "5G",
      "spark.jsl.settings.pretrained.cache_folder": tempPath("spark", "cache_pretrained"),
      "spark.jsl.settings.storage.cluster_tmp_dir": tempPath("spark", "annotator_logs"),
      "spark.driver.supervise": "true",
  }

  # See https://github.com/JohnSnowLabs/spark-nlp/blob/master/python/sparknlp/__init__.py#L139C8-L139C101
  try:
    if '_instantiatedSession' in dir(
        sparknlp.SparkSession) and sparknlp.SparkSession._instantiatedSession is not None:  # type: ignore
      print("Restarting Spark NLP session")
      sparknlp.SparkSession._instantiatedSession.stop()  # type: ignore
    return sparknlp.start(  # type: ignore
        params=SPARKNLP_PARAMS,
        gpu=gpu,
        apple_silicon=apple_silicon,
        aarch64=aarch64,
        memory=memory)
  except:
    print("Unable to recover Spark NLP session. Restarting.")
    exit()  # spark session is busted due to timeout, kill the session
