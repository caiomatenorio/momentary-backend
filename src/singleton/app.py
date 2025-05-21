from marshmallow import ValidationError

from src.api.blueprint.api_bp import api_bp
from src.api.error_handler import (
    handle_http_exception,
    handle_unauthorized_exception,
    handle_validation_error,
)
from src.common.exception.http.http_exception import HttpException
from src.common.exception.http.unauthorized_exception import UnauthorizedException
from src.config import create_app
from src.singleton.db import db
from src.singleton.marshmallow import marshmallow
from src.singleton.migrate import migrate
from src.singleton.scheduler import scheduler
from src.singleton.socketio import socketio
from src.socket.namespace.chat_namespace import ChatNamespace

error_handlers = {
    HttpException: handle_http_exception,
    UnauthorizedException: handle_unauthorized_exception,
    ValidationError: handle_validation_error,
}

namespaces = {
    "/sockets/chats": ChatNamespace,
}

app = create_app(
    db,
    migrate,
    socketio,
    marshmallow,
    scheduler,
    api_bp,
    error_handlers,
    namespaces,
)
