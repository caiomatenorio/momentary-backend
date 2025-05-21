from src.common.exception.common_exception import CommonException


class SocketSessionNotFoundException(CommonException):
    def __init__(self) -> None:
        super().__init__("Socket session was not found.")
