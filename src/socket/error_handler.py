from flask_socketio import disconnect, emit
from marshmallow import ValidationError

from src.common.exception.http.http_exception import HttpException
from src.common.exception.socket_session_not_found import SocketSessionNotFoundException
from src.service import socket_service
from src.socket.response_body import ResponseBody


def error_handler(e):

    if isinstance(e, HttpException):
        emit("error_response", ResponseBody(e.message).to_dict())
        return
    if isinstance(e, SocketSessionNotFoundException):
        disconnect()
        return
    if isinstance(e, ValidationError):
        emit("error_response", ResponseBody("Validation error.", e.messages).to_dict())
        return
    if isinstance(e, Exception):
        emit("error_response", ResponseBody("An unknown error occurred.").to_dict())
        print(e)
        return
