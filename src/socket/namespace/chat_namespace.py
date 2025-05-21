from flask_socketio import Namespace

from src.service import chat_service
from src.socket.decorator.handle_auth_namespace_connection import (
    handle_auth_namespace_connection,
)
from src.socket.decorator.handle_auth_namespace_disconnection import (
    handle_auth_namespace_disconnection,
)


class ChatNamespace(Namespace):
    @handle_auth_namespace_connection
    def on_connect(self):
        chat_service.connect_to_all_chats()

    @handle_auth_namespace_disconnection
    def on_disconnect(self): ...
