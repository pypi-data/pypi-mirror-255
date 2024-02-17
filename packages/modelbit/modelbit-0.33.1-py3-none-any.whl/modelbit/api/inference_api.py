from typing import Optional, Any, Union, Dict
from modelbit.error import UserFacingError
import re, requests, json
from requests import ConnectionError
import logging


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


def callDeployment(region: str, workspace: Optional[str], branch: Optional[str], deployment: str,
                   version: Union[str, int], data: Any, apiKey: Optional[str],
                   timeoutSeconds: Optional[int]) -> Dict[str, Any]:

  _assertValid(region, "region")
  _assertValid(workspace, "workspace", "Supply the 'workspace' parameter or set the MB_WORKSPACE_NAME envvar")
  _assertValid(branch, "branch")
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

  url = f"https://{workspace}.{region}.modelbit.com/v1/{deployment}/{branch}/{strVersion}"
  try:
    mbTimeoutParam = {"timeout_seconds": timeoutSeconds} if timeoutSeconds else {}
    rqTimeoutParam = timeoutSeconds + 5 if timeoutSeconds else None
    return requests.post(url,
                         headers=_headers(apiKey),
                         data=json.dumps({
                             "data": data,
                             **mbTimeoutParam,
                         }),
                         timeout=rqTimeoutParam).json()
  except ConnectionError as err:
    logging.error(err)
    raise UserFacingError(f"Unable to connect to '{url}'.")
