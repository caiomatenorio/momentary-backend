from ..decorators.handle_socket_unauthentication import handle_socket_unauthentication
from ..decorators.requires_socket_authentication import requires_socket_authentication
from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..libs.socketio import socketio
from ..services import socket_service


@socketio.event(namespace="/message")
@requires_socket_authentication
def connect(auth):
    pass


@socketio.event(namespace="/message")
@handle_socket_unauthentication
def disconnect():
    pass
