from flask_socketio import Namespace, send

from src.socket.decorator.requires_auth import requires_auth


@requires_auth
class MessageNamespace(Namespace):
    def on_message(self, data):
        send(data)
