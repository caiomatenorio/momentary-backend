from flask_socketio import send

from src.service import session_service
from src.singleton.socketio import socketio
from src.socket.decorator.handle_private_namespace_disconnection import (
    handle_private_namespace_disconnection,
)
from src.socket.decorator.handle_socket_with_auth_connection import (
    handle_private_namespace_connection,
)
from src.socket.decorator.requires_auth import requires_auth

namespace = "/sockets/messages"


@socketio.event(namespace=namespace)
@handle_private_namespace_connection
def connect():
    pass


@socketio.event(namespace=namespace)
@requires_auth
def message(data):
    tokens = session_service.get_new_tokens(in_json=True)
    send(tokens)


@socketio.event(namespace=namespace)
@handle_private_namespace_disconnection
def disconnect():
    pass
