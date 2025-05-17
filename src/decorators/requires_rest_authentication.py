from functools import wraps
from typing import Callable

from ..services import session_service


def requires_rest_authentication(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        session_service.validate_session()
        return function(*args, **kwargs)

    return wrapper
