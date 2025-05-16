import os

from dotenv import load_dotenv

from .exceptions.env_not_defined_exception import EnvNotDefinedException

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
        self._MESSAGE_TTL_SECS = int(self._get_env_var("MESSAGE_TTL_SECS"))
        self._REDIS_URL = self._get_env_var("REDIS_URL")
        self._REDIS_TOKEN = self._get_env_var("REDIS_TOKEN")

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

    @property
    def MESSAGE_TTL_SECS(self) -> str:
        return self._MESSAGE_TTL_SECS

    @property
    def REDIS_URL(self) -> str:
        return self._REDIS_URL

    @property
    def REDIS_TOKEN(self) -> str:
        return self._REDIS_TOKEN

    def _get_env_var(self, key: str) -> str:
        value = os.getenv(key)

        if not value:
            raise EnvNotDefinedException(key)

        return value


env = Env()
