from ..common_exception import CommonException


class HttpException(CommonException):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self._status_code = status_code

    @property
    def status_code(self) -> int:
        return self._status_code
