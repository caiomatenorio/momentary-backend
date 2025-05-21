from typing import Optional, overload

from flask import Request, request
from flask_socketio import disconnect, emit

from src.common.dto.session_data import SessionData
from src.common.dto.user_data import UserData
from src.common.exception.http.unauthorized_exception import UnauthorizedException
from src.common.exception.namespace_access_outside_socket_exception import (
    NamespaceAccessOutsideSocketException,
)
from src.common.exception.session_expired_exception import SessionExpiredException
from src.common.exception.session_not_found_exception import SessionNotFoundException
from src.common.exception.sid_access_outside_socket_exception import (
    SidAccessOutsideSocketException,
)
from src.common.exception.socket_session_not_found import SocketSessionNotFoundException
from src.service import session_service
from src.singleton.redis import redis


def get_sid(request: Request) -> str:
    sid: str | None = request.sid  # type: ignore

    if sid is None:
        raise SidAccessOutsideSocketException()
    return sid


def get_namespace(request: Request) -> str:
    namespace: str | None = request.namespace  # type: ignore

    if namespace is None:
        raise NamespaceAccessOutsideSocketException()
    return namespace


def set_socket_session(request: Request) -> None:
    session_data = session_service.get_current_session_data().flatten()
    redis.hset(
        f"socket_session:{get_sid(request)}",
        mapping=session_data,
    )


def get_socket_session(request: Request) -> Optional[tuple[str, SessionData]]:
    socket_session: dict = redis.hgetall(f"socket_session:{get_sid(request)}")  # type: ignore

    if socket_session:
        refresh_token = socket_session.pop("refresh_token", None)
        session_data = None

        try:
            session_data = SessionData.from_flattened(socket_session)
        except Exception:
            ...

        if refresh_token and session_data:
            return refresh_token, session_data


def get_socket_session_or_raise(request: Request) -> tuple[str, SessionData]:
    socket_session = get_socket_session(request)

    if socket_session is None:
        raise SocketSessionNotFoundException()
    return socket_session


def delete_socket_session(request: Request) -> None:
    redis.delete(f"socket_session:{get_sid(request)}")
