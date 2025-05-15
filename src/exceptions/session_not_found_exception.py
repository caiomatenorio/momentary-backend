class SessionNotFoundException(Exception):
    def __init__(self):
        self.message = "Session not found"
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
