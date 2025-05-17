from .common_exception import CommonException


class SessionExpiredException(CommonException):
    def __init__(self) -> None:
        super().__init__("Session has expired")
