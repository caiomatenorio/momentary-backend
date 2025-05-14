class EnvNotDefinedError(Exception):
    def __init__(self, key) -> None:
        self.key = key
        self.message = f"Environment variable '{key}' not defined"

        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
