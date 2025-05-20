import os
from typing import Literal

from dotenv import load_dotenv

from src.common.exception.env_not_defined_exception import EnvNotDefinedException

load_dotenv()


class Env:
    def __init__(self) -> None:
        flask_env: Literal["development", "production"] | str = self._get_env_var(
            "FLASK_ENV"
        )

        if flask_env != "development" and flask_env != "production":
            raise EnvNotDefinedException("FLASK_ENV")

        self._DB_URL = self._get_env_var("DB_URL")
        self._SECRET_KEY = self._get_env_var("SECRET_KEY")
        self._SESSION_EXPIRATION_SECS = int(
            self._get_env_var("SESSION_EXPIRATION_SECS")
        )
        self._JWT_SECRET_KEY = self._get_env_var("JWT_SECRET_KEY")
        self._JWT_EXPIRATION_SECS = int(self._get_env_var("JWT_EXPIRATION_SECS"))
        self._FLASK_ENV = flask_env
        self._MESSAGE_TTL_SECS = int(self._get_env_var("MESSAGE_TTL_SECS"))
        self._REDIS_URL = self._get_env_var("REDIS_URL")

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
    def FLASK_ENV(self) -> Literal["development", "production"]:
        return self._FLASK_ENV

    @property
    def MESSAGE_TTL_SECS(self) -> int:
        return self._MESSAGE_TTL_SECS

    @property
    def REDIS_URL(self) -> str:
        return self._REDIS_URL

    @staticmethod
    def _get_env_var(key: str) -> str:
        value = os.getenv(key)

        if not value:
            raise EnvNotDefinedException(key)

        return value


env = Env()
