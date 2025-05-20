class CommonException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return f"{self.name}: {self.message}"
