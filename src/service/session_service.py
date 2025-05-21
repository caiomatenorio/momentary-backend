import json
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, Union, overload
from uuid import UUID

import jwt
from flask import Response, g, request

from src.common.dto.jwt_payload import JwtPayload
from src.common.dto.session_data import SessionData
from src.common.dto.user_data import UserData
from src.common.exception.http.unauthorized_exception import UnauthorizedException
from src.common.exception.session_expired_exception import SessionExpiredException
from src.common.exception.session_not_found_exception import SessionNotFoundException
from src.model.session import Session
from src.service import user_service
from src.singleton.db import db
from src.singleton.env import env


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
def get_new_tokens(*, in_json: Literal[True]) -> Optional[str]: ...


def get_new_tokens(
    *,
    in_json: bool = False,
) -> Union[Optional[str], tuple[Optional[str], Optional[str]]]:
    auth_token = g.get("auth_token")
    refresh_token = g.get("refresh_token")

    if in_json:
        return (
            json.dumps({"auth_token": auth_token, "refresh_token": refresh_token})
            if auth_token and refresh_token
            else None
        )

    return auth_token, refresh_token


def add_session_headers(response: Response) -> None:
    auth_token, refresh_token = get_new_tokens()

    if auth_token and refresh_token:
        response.headers.add("Authorization", f"Bearer {auth_token}|{refresh_token}")


def add_clear_session_headers(response: Response) -> None:
    response.headers.add("Authorization", None)


def extract_session_tokens_from_request() -> tuple[Optional[str], Optional[str]]:
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

    if session:
        try:
            validate_not_expired_session(session)
            return session
        except SessionExpiredException:
            pass


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

    if session:
        try:
            validate_not_expired_session(session)
            return session
        except SessionExpiredException:
            pass


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


def validate_session(*, for_socket: bool = False) -> None:
    auth_token, refresh_token = extract_session_tokens_from_request()

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


@overload
def validate_not_expired_session(session: Session) -> None: ...


@overload
def validate_not_expired_session(
    session: Session,
    *,
    nested: Literal[True],
) -> None: ...


def validate_not_expired_session(session: Session, *, nested: bool = False) -> None:
    if session.expires_at < datetime.now(timezone.utc):
        if nested:
            delete_session(session=session, nested=True)
        else:
            delete_session(session=session)

        raise SessionExpiredException()


def refresh_session(refresh_token: str) -> tuple[str, str]:
    with db.session.begin():
        session = get_session_by_refresh_token_or_raise(refresh_token, for_update=True)
        validate_not_expired_session(session, nested=True)

        session.refresh_token = Session.generate_refresh_token()
        session.expires_at = Session.calculate_expiration()
        session.updated_at = datetime.now(timezone.utc)
        db.session.add(session)

        user = user_service.get_user_by_id_or_raise(session.user_id)
        jwt = create_jwt(session.id, user.id, user.username, user.name)

        return jwt, session.refresh_token


@overload
def delete_session(*, session: Session) -> None: ...


@overload
def delete_session(*, session: Session, nested: Literal[True]) -> None: ...


@overload
def delete_session(*, session_id: UUID) -> None: ...


@overload
def delete_session(*, session_id: UUID, nested: Literal[True]) -> None: ...


def delete_session(
    *,
    session: Optional[Session] = None,
    session_id: Optional[UUID] = None,
    nested: bool = False,
) -> None:
    begin_session = db.session.begin_nested if nested else db.session.begin

    with begin_session():
        session = get_session_by_id_or_raise(session_id) if session_id else session
        db.session.delete(session)


def delete_current_session() -> None:
    session_id = get_current_session_data().session_id
    delete_session(session_id=session_id)


def clean_expired_sessions() -> None:
    with db.session.begin():
        expired_sessions = (
            db.session.query(Session)
            .filter(Session.expires_at < datetime.now(timezone.utc))
            .with_for_update()
            .all()
        )

        for expired_session in expired_sessions:
            delete_session(session=expired_session, nested=True)
