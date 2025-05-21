from src.common.exception.http.http_exception import HttpException


class UsernameAlreadyInUseException(HttpException):
    def __init__(self) -> None:
        super().__init__(409, "Username already in use.")
