from functools import wraps
from typing import Callable

from flask import request

from ..services import socket_service


def handle_socket_with_auth_disconnection(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        socket_service.delete_socket_session(request)
        return function(*args, **kwargs)

    return wrapper
