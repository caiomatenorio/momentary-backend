from functools import wraps
from typing import Callable

from flask import request

from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..services import session_service, socket_service


def handle_socket_with_auth_connection(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            session_service.validate_session(request, for_socket=True)
        except UnauthorizedException:
            # Refuse connection
            return False

        socket_service.set_socket_session(request)
        return function(*args, **kwargs)

    return wrapper
