from src.common.exception.http.http_exception import HttpException


class UserNotFoundException(HttpException):
    def __init__(self):
        super().__init__(404, "User not found.")
