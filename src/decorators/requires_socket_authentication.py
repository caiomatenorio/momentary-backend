from functools import wraps
from typing import Callable

from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..services import session_service, socket_service


def requires_socket_authentication(function: Callable) -> Callable:
    """
    Decorator to require socket authentication for an event handler (generally connect). The function requires the
    `auth` parameter to be passed in the event handler.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        # Get the auth object from the arguments passed to the function
        auth = kwargs.get("auth")
        auth_token = auth.get("auth_token") if auth else None
        refresh_token = auth.get("refresh_token") if auth else None

        if not auth_token or not refresh_token:
            return False

        try:
            session_service.validate_session(
                auth_token=auth_token,
                refresh_token=refresh_token,
            )
        except UnauthorizedException:
            return False

        socket_service.store_socket_session_data()

        # Call the original function with the provided arguments
        return function(*args, **kwargs)

    return wrapper
