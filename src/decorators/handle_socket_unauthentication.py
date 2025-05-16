from functools import wraps

from flask import g

from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..services import session_service, socket_service


def handle_socket_unauthentication(function: callable) -> callable:
    """
    Decorator to handle socket unauthentication by refreshing the session if needed. It stores the new auth and refresh
    tokens to return to the client.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        user_data = socket_service.get_socket_session_data_by_sid()

        if user_data and (session_id := user_data.get("session_id")):
            try:
                g.new_auth_token, g.new_refresh_token = session_service.refresh_session(
                    session_id=session_id
                )
            except UnauthorizedException:
                pass

        # Call the original function with the provided arguments
        return function(*args, **kwargs)

    return wrapper
