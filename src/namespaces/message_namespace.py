import json

from flask_socketio import send

from ..decorators.handle_socket_with_auth_connection import (
    handle_socket_with_auth_connection,
)
from ..decorators.handle_socket_with_auth_disconnection import (
    handle_socket_with_auth_disconnection,
)
from ..decorators.requires_socket_auth import requires_socket_auth
from ..libs.socketio import socketio
from ..services import session_service


@socketio.event(namespace="/sockets/messages")
@handle_socket_with_auth_connection
def connect():
    pass


@socketio.event(namespace="/sockets/messages")
@requires_socket_auth
def message(data):
    tokens = session_service.get_new_tokens(in_json=True)
    send(tokens)


@socketio.event(namespace="/sockets/messages")
@handle_socket_with_auth_disconnection
def disconnect():
    pass
