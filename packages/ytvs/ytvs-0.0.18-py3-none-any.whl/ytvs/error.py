from dataclasses import dataclass
from typing import Optional


class ErrorCode:
    HTTP_ERROR = 10000
    MISSING_PARAMS = 10001
    INVALID_PARAMS = 10002
    NEED_AUTHORIZATION = 10003
    AUTHORIZE_URL_FIRST = 10004


@dataclass
class ErrorMessage:
    status_code: Optional[int] = None
    message: Optional[str] = None

