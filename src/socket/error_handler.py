from src.common.exception.socket_session_not_found import SocketSessionNotFoundException
from src.singleton.socketio import socketio


@socketio.on_error_default
def default_error_handler(e):
    if isinstance(e, SocketSessionNotFoundException):
        pass
    else:
        print(e)
