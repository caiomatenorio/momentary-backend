from src.exceptions.common_exception import CommonException


class SidAccessOutsideSocketException(CommonException):
    def __init__(self) -> None:
        super().__init__("Tried to access request.sid outside socket connection.")
