from functools import wraps
from typing import Callable

from flask import request

from src.service import socket_service


def requires_auth(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        ok = socket_service.refresh_socket_session(request)

        if not ok:
            return False
        return function(*args, **kwargs)

    return wrapper
