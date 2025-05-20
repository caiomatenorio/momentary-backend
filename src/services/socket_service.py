import json
from typing import Optional, overload

from flask import Request
from flask_socketio import disconnect, emit

from src.dtos.user_data import UserData

from ..dtos.session_data import SessionData
from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..exceptions.namespace_access_outside_socket_exception import (
    NamespaceAccessOutsideSocketException,
)
from ..exceptions.session_expired_exception import SessionExpiredException
from ..exceptions.session_not_found_exception import SessionNotFoundException
from ..exceptions.sid_access_outside_socket_exception import (
    SidAccessOutsideSocketException,
)
from ..exceptions.socket_session_not_found import SocketSessionNotFoundException
from ..libs.redis import redis
from ..services import session_service


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


@overload
def set_socket_session(request: Request) -> None: ...


@overload
def set_socket_session(request: Request, refresh_token: str) -> None: ...


def set_socket_session(request: Request, refresh_token: Optional[str] = None) -> None:
    if refresh_token is None:
        _, refresh_token = session_service.extract_session_tokens_from_request(request)

        if refresh_token is None:  # If it's still None
            raise UnauthorizedException()

        session_data = session_service.get_current_session_data().flatten()
    else:
        session = session_service.get_session_by_refresh_token_or_raise(refresh_token)
        session_data = SessionData(
            session_id=session.id,
            user_data=UserData(
                user_id=session.user_id,
                username=session.user.username,
                name=session.user.name,
            ),
        ).flatten()

    redis.hset(
        f"socket_session:{get_sid(request)}",
        mapping={
            "refresh_token": refresh_token,
            **session_data,
        },
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


def refresh_socket_session(request: Request) -> bool:
    try:
        refresh_token, _ = get_socket_session_or_raise(request)
        auth_token, refresh_token = session_service.refresh_session(refresh_token)
        set_socket_session(request, refresh_token)
        session_service.set_new_tokens(
            auth_token=auth_token,
            refresh_token=refresh_token,
        )
        return True
    except (
        SocketSessionNotFoundException,
        SessionNotFoundException,
        SessionExpiredException,
    ):
        disconnect()
        return False


def delete_socket_session(request: Request) -> None:
    redis.delete(f"socket_session:{get_sid(request)}")
