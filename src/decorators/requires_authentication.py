from functools import wraps

from ..services import session_service


def requires_authentication(function: callable) -> callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        request = kwargs.get("request")

        if not request:
            raise ValueError("Request object is required")

        new_tokens = session_service.validate_session(request)
        kwargs["new_tokens"] = new_tokens

        return function(*args, **kwargs)

    return wrapper
