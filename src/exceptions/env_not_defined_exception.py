from .common_exception import CommonException


class EnvNotDefinedException(CommonException):
    def __init__(self, key) -> None:
        self._key = key
        super().__init__(f"Environment variable '{key}' not defined")

    @property
    def key(self) -> str:
        return self._key
