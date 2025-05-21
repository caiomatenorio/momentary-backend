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


@overload
def get_socket_session() -> Optional[SessionData]: ...


@overload
def get_socket_session(*, raise_: Literal[True]) -> SessionData: ...


@overload
def get_socket_session(*, disconnect_: Literal[True]) -> SessionData: ...


@overload
def get_socket_session(
    *,
    raise_: bool,
    disconnect_: bool,
) -> Optional[SessionData]: ...


def get_socket_session(
    *,
    raise_: bool = False,
    disconnect_: bool = False,
) -> Optional[SessionData]:
    socket_session: dict = redis.hgetall(f"socket_session:{get_sid()}")  # type: ignore

    if socket_session:
        session_data = None

        try:
            session_data = SessionData.from_flattened(socket_session)
        except Exception:
            ...

        if session_data:
            return session_data
        elif raise_:
            raise SocketSessionNotFoundException()
        elif disconnect_:
            emit("session_expired", {"message": "Sign in again to reconnect."})
            disconnect()
            raise SocketSessionNotFoundException()


def delete_socket_session() -> None:
    redis.delete(f"socket_session:{get_sid()}")


def connect_to_room(room: str) -> None:
    join_room(room)
