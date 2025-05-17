import asyncio
from functools import wraps
from typing import Callable

from flask import g

from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..services import session_service, socket_service


def handle_socket_unauthentication(function: Callable) -> Callable:
    """
    Decorator to handle socket unauthentication by refreshing the session if needed. It stores the new auth and refresh
    tokens to return to the client.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        session_data = asyncio.run(socket_service.get_socket_session_data_by_sid())

        if session_data and (session_id := session_data.session_id):
            try:
                session_service.set_new_tokens(
                    *session_service.refresh_session(session_id=session_id)
                )
            except UnauthorizedException:
                pass

        # Call the original function with the provided arguments
        return function(*args, **kwargs)

    return wrapper
