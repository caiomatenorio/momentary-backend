from src.common.exception.http.http_exception import HttpException


class DirectChatAlreadyExistsException(HttpException):
    def __init__(self) -> None:
        super().__init__(409, "Direct chat already exists.")
