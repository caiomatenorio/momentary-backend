from src.common.exception.http.http_exception import HttpException


class InvalidCredentialsException(HttpException):
    def __init__(self) -> None:
        super().__init__(401, "Invalid credentials provided.")
