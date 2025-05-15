import os

from dotenv import load_dotenv

from src.common.errors.env_not_defined_error import EnvNotDefinedError

load_dotenv()


class Env:
    def __init__(self) -> None:
        self._DB_URL = self._get_env_var("DB_URL")
        self._SECRET_KEY = self._get_env_var("SECRET_KEY")
        self._SESSION_EXPIRATION_SECS = int(
            self._get_env_var("SESSION_EXPIRATION_SECS")
        )
        self._JWT_SECRET_KEY = self._get_env_var("JWT_SECRET_KEY")
        self._JWT_EXPIRATION_SECS = int(self._get_env_var("JWT_EXPIRATION_SECS"))
        self._ENV = self._get_env_var("ENV")

    @property
    def DB_URL(self) -> str:
        return self._DB_URL

    @property
    def SECRET_KEY(self) -> str:
        return self._SECRET_KEY

    @property
    def SESSION_EXPIRATION_SECS(self) -> int:
        return self._SESSION_EXPIRATION_SECS

    @property
    def JWT_SECRET_KEY(self) -> str:
        return self._JWT_SECRET_KEY

    @property
    def JWT_EXPIRATION_SECS(self) -> int:
        return self._JWT_EXPIRATION_SECS

    @property
    def ENV(self) -> str:
        return self._ENV

    def _get_env_var(key: str) -> str:
        value = os.getenv(key)

        if not value:
            raise EnvNotDefinedError(key)

        return value


env = Env()
