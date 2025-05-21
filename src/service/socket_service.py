from typing import Literal, Optional, overload

from flask import request
from flask_socketio import disconnect, emit, join_room

from src.common.dto.session_data import SessionData
from src.common.exception.namespace_access_outside_socket_exception import (
    NamespaceAccessOutsideSocketException,
)
from src.common.exception.sid_access_outside_socket_exception import (
    SidAccessOutsideSocketException,
)
from src.common.exception.socket_session_not_found import SocketSessionNotFoundException
from src.service import session_service
from src.singleton.redis import redis


def get_sid() -> str:
    sid: str | None = request.sid  # type: ignore

    if sid is None:
        raise SidAccessOutsideSocketException()
    return sid


def get_namespace() -> str:
    namespace: str | None = request.namespace  # type: ignore

    if namespace is None:
        raise NamespaceAccessOutsideSocketException()
    return namespace


def set_socket_session() -> None:
    session_data = session_service.get_current_session_data().flatten()
    key = f"socket_session:{get_sid()}"
    redis.hset(key, mapping=session_data)
    redis.expire(key, 60 * 60 * 24 * 30)  # 30 days


def get_socket_session() -> Optional[SessionData]:
    socket_session: dict = redis.hgetall(f"socket_session:{get_sid()}")  # type: ignore

    if socket_session:
        try:
            session_data = SessionData.from_flattened(socket_session)
            return session_data
        except Exception:
            pass


def get_socket_session_or_raise() -> SessionData:
    socket_session = get_socket_session()

    if socket_session is None:
        raise SocketSessionNotFoundException()
    return socket_session


def delete_socket_session() -> None:
    redis.delete(f"socket_session:{get_sid()}")


def connect_to_room(room: str) -> None:
    join_room(room)
