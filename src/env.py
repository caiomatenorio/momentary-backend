import os

from dotenv import load_dotenv

from src.common.errors.env_not_defined_error import EnvNotDefinedError

load_dotenv()


def get_env_var(key: str) -> str:
    value = os.getenv(key)

    if not value:
        raise EnvNotDefinedError(key)

    return value


env = {
    "DB_URL": get_env_var("DB_URL"),
    "SECRET_KEY": get_env_var("SECRET_KEY"),
    "SESSION_EXPIRATION_SECS": int(get_env_var("SESSION_EXPIRATION_SECS")),
    "JWT_SECRET_KEY": get_env_var("JWT_SECRET_KEY"),
    "JWT_EXPIRATION_SECS": int(get_env_var("JWT_EXPIRATION_SECS")),
    "ENV": get_env_var("ENV"),
}
