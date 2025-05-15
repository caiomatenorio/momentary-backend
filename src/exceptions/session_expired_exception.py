class SessionExpiredException(Exception):
    def __init__(self) -> None:
        self.message = "Session has expired"
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
