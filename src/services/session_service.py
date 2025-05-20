import json
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, Union, overload
from uuid import UUID

import jwt
from flask import Request, Response, g

from ..dtos.jwt_payload import JwtPayload
from ..dtos.session_data import SessionData
from ..dtos.user_data import UserData
from ..env import env
from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..exceptions.session_expired_exception import SessionExpiredException
from ..exceptions.session_not_found_exception import SessionNotFoundException
from ..libs.sqlalchemy import db
from ..models.session import Session
from . import refresh_token_service, user_service


def create_session(user_id: UUID) -> Session:
    with db.session.begin_nested():
        session = Session(user_id=user_id)  # type: ignore
        db.session.add(session)
    return session


def create_jwt(session_id: UUID, user_id: UUID, username: str, name: str) -> str:
    jwt_expiration_secs = env.JWT_EXPIRATION_SECS

    now = datetime.now(timezone.utc)
    payload = JwtPayload(
        data=SessionData(
            session_id=session_id,
            user_data=UserData(
                user_id=user_id,
                username=username,
                name=name,
            ),
        ),
        exp=int((now + timedelta(seconds=jwt_expiration_secs)).timestamp()),
        iat=int(now.timestamp()),
    )

    return jwt.encode(payload.to_dict(), env.JWT_SECRET_KEY, algorithm="HS256")


def decode_jwt(token: str) -> JwtPayload:
    try:
        decoded_jwt = jwt.decode(token, env.JWT_SECRET_KEY, algorithms=["HS256"])
        payload = JwtPayload.from_dict(decoded_jwt)
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise UnauthorizedException()


def set_new_tokens(auth_token: str, refresh_token: str) -> None:
    g.auth_token = auth_token
    g.refresh_token = refresh_token


@overload
def get_new_tokens() -> tuple[Optional[str], Optional[str]]: ...


@overload
def get_new_tokens(*, in_json: Literal[True]) -> str: ...


def get_new_tokens(
    *,
    in_json: bool = False,
) -> Union[str, tuple[Optional[str], Optional[str]]]:
    auth_token = g.get("auth_token")
    refresh_token = g.get("refresh_token")

    if in_json:
        return json.dumps({"auth_token": auth_token, "refresh_token": refresh_token})

    return auth_token, refresh_token


def add_session_headers(response: Response) -> None:
    auth_token, refresh_token = get_new_tokens()

    if auth_token and refresh_token:
        response.headers.add("Authorization", f"Bearer {auth_token}|{refresh_token}")


def add_clear_session_headers(response: Response) -> None:
    response.headers.add("Authorization", None)


def extract_session_tokens_from_request(
    request: Request,
) -> tuple[Optional[str], Optional[str]]:
    auth_token, refresh_token = None, None
    authorization = request.headers.get("Authorization")

    if authorization:
        authorization = authorization.removeprefix("Bearer ").split("|", 1)

        if len(authorization) == 2 and all(authorization):
            auth_token, refresh_token = authorization

    return auth_token, refresh_token


@overload
def set_current_session_data(*, auth_token: str) -> None: ...


@overload
def set_current_session_data(*, refresh_token) -> None: ...


def set_current_session_data(
    *, auth_token: Optional[str] = None, refresh_token: Optional[str] = None
) -> None:
    if auth_token:
        payload_data = decode_jwt(auth_token).data

        g.current_session_id = payload_data.session_id
        g.current_user_id = payload_data.user_data.user_id
        g.current_username = payload_data.user_data.username
        g.current_name = payload_data.user_data.name
    elif refresh_token:
        session = get_session_by_refresh_token_or_raise(refresh_token)

        g.current_session_id = session.id
        g.current_user_id = session.user_id
        g.current_username = session.user.username
        g.current_name = session.user.name
    else:
        ValueError("It is required to insert either auth token or refresh token.")


def get_current_session_data() -> SessionData:
    session_id: Optional[UUID] = g.get("current_session_id")
    user_id: Optional[UUID] = g.get("current_user_id")
    username: Optional[str] = g.get("current_username")
    name: Optional[str] = g.get("current_name")

    if not session_id or not user_id or not username or not name:
        raise UnauthorizedException()

    return SessionData(
        session_id=session_id,
        user_data=UserData(
            user_id=user_id,
            username=username,
            name=name,
        ),
    )


def get_session_by_id(
    session_id: UUID,
    *,
    for_update: bool = False,
) -> Optional[Session]:
    query = db.session.query(Session).filter_by(id=session_id)

    if for_update:
        query = query.with_for_update()

    session = query.first()
    return session


def get_session_by_id_or_raise(
    session_id: UUID,
    *,
    for_update: bool = False,
) -> Session:
    session = get_session_by_id(session_id, for_update=for_update)

    if not session:
        raise SessionNotFoundException()
    return session


def get_session_by_refresh_token(
    refresh_token: str,
    *,
    for_update: bool = False,
) -> Optional[Session]:
    query = db.session.query(Session).filter_by(refresh_token=refresh_token)

    if for_update:
        query = query.with_for_update()

    session = query.first()
    return session


def get_session_by_refresh_token_or_raise(
    refresh_token: str,
    *,
    for_update: bool = False,
) -> Session:
    session = get_session_by_refresh_token(refresh_token, for_update=for_update)

    if session is None:
        raise SessionNotFoundException()
    return session


def validate_refresh_token(refresh_token: str) -> None:
    get_session_by_refresh_token_or_raise(refresh_token)


def signin(username: str, password: str) -> None:
    with db.session.begin():
        user_service.validate_credentials(username, password, for_update=True)
        user = user_service.get_user_by_username_or_raise(username, for_update=True)
        session = create_session(user.id)
        auth_token = create_jwt(session.id, user.id, user.username, user.name)
        set_new_tokens(auth_token, session.refresh_token)


def validate_session(request: Request, *, for_socket: bool = False) -> None:
    auth_token, refresh_token = extract_session_tokens_from_request(request)

    if not for_socket and auth_token:
        try:
            set_current_session_data(auth_token=auth_token)
            return
        except UnauthorizedException:  # If token is invalid or expired, try to refresh
            pass

    if refresh_token:
        try:
            if for_socket:
                validate_refresh_token(refresh_token)
                set_current_session_data(refresh_token=refresh_token)
            else:
                auth_token, refresh_token = refresh_session(refresh_token=refresh_token)
                set_current_session_data(auth_token=auth_token)
                set_new_tokens(auth_token, refresh_token)
            return
        except (SessionNotFoundException, SessionExpiredException):
            pass

    raise UnauthorizedException()


def refresh_session(refresh_token: str) -> tuple[str, str]:
    with db.session.begin():
        session = get_session_by_refresh_token_or_raise(refresh_token, for_update=True)

        if session.expires_at < datetime.now(timezone.utc):
            with db.session.begin_nested():
                db.session.delete(session)
            raise SessionExpiredException()

        session.refresh_token = refresh_token_service.generate_refresh_token()
        session.expires_at = Session.calculate_expiration()
        session.updated_at = datetime.now(timezone.utc)
        db.session.add(session)
        user = user_service.get_user_by_id_or_raise(session.user_id)
        jwt = create_jwt(session.id, user.id, user.username, user.name)

        return jwt, session.refresh_token


def signout() -> None:
    with db.session.begin():
        session_id = get_current_session_data().session_id
        session = get_session_by_id_or_raise(session_id)
        db.session.delete(session)


def clean_expired_sessions() -> None:
    with db.session.begin():
        expired_sessions = (
            db.session.query(Session)
            .filter(Session.expires_at < datetime.now(timezone.utc))
            .with_for_update()
            .all()
        )

        for expired_session in expired_sessions:
            db.session.delete(expired_session)
            db.session.delete(expired_session)
