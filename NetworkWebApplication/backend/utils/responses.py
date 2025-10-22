from typing import Any, Dict, Optional


# PUBLIC_INTERFACE
def success(data: Optional[Any] = None, message: str = "ok", **kwargs) -> Dict[str, Any]:
    """Return a standardized success response payload."""
    resp = {"status": "success", "message": message}
    if data is not None:
        resp["data"] = data
    if kwargs:
        resp.update(kwargs)
    return resp


# PUBLIC_INTERFACE
def error(message: str, code: Optional[str] = None, details: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
    """Return a standardized error response payload."""
    resp = {"status": "error", "message": message}
    if code:
        resp["code"] = code
    if details is not None:
        resp["details"] = details
    if kwargs:
        resp.update(kwargs)
    return resp
