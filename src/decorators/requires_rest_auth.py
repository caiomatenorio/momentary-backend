from functools import wraps
from typing import Callable

from flask import request

from ..services import session_service


def requires_rest_auth(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        session_service.validate_session(request)
        return function(*args, **kwargs)

    return wrapper
