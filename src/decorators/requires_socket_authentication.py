from functools import wraps
from typing import Callable

from flask import request

from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..services import session_service, socket_service


def requires_socket_authentication(function: Callable) -> Callable:
    """
    Decorator to require socket authentication for an event handler (generally connect). The function requires the
    `auth` parameter to be passed in the event handler.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):

        try:
            session_service.validate_session()
        except UnauthorizedException:
            return False

        socket_service.store_socket_session_data()
        return function(*args, **kwargs)

    return wrapper
