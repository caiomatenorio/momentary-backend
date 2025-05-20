from src.exceptions.common_exception import CommonException


class NamespaceAccessOutsideSocketException(CommonException):
    def __init__(self) -> None:
        super().__init__("Tried to access request.namespace outside socket connection.")
