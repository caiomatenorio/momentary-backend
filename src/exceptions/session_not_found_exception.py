from .common_exception import CommonException


class SessionNotFoundException(CommonException):
    def __init__(self):
        super().__init__("Session not found")
