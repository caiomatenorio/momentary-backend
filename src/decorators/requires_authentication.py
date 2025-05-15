from functools import wraps

from flask import Request

from ..services import session_service


def requires_authentication(request: Request):
    def decorator(function: callable) -> callable:
        @wraps(function)
        def wrapper(*args, **kwargs):
            session_service.validate_session(request)
            return function(*args, **kwargs)

        return wrapper

    return decorator
