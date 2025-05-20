from src.common.exception.http.http_exception import HttpException


class UnauthorizedException(HttpException):
    def __init__(self):
        super().__init__(401, "Unauthorized access.")
