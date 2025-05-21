from src.common.exception.http.http_exception import HttpException


class ChatNotFoundException(HttpException):
    def __init__(self):
        super().__init__(404, "Chat not found.")
