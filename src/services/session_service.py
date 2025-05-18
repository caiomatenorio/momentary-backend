from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from flask import Request, Response, g, request
from sqlalchemy.exc import IntegrityError

from src.dtos.jwt_payload import JwtPayload
from src.dtos.session_data import SessionData
from src.dtos.user_data import UserData

from ..env import env
from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..exceptions.session_expired_exception import SessionExpiredException
from ..exceptions.session_not_found_exception import SessionNotFoundException
from ..libs.sqlalchemy import db
from ..models.session import Session
from ..models.user import User
from . import user_service


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


def is_jwt_valid(jwt: str) -> bool:
    try:
        decode_jwt(jwt)
        return True
    except UnauthorizedException:
        return False


def set_new_tokens(auth_token: str, refresh_token: str) -> None:
    g.new_auth_token = auth_token
    g.new_refresh_token = refresh_token


def get_new_tokens() -> tuple[Optional[str], Optional[str]]:
    new_auth_token = g.get("new_auth_token")
    new_refresh_token = g.get("new_refresh_token")

    return new_auth_token, new_refresh_token


def add_session_cookies(response: Response) -> None:
    new_auth_token, new_refresh_token = get_new_tokens()

    if new_auth_token and new_refresh_token:
        response.set_cookie(
            "auth_token",
            new_auth_token,
            max_age=env.JWT_EXPIRATION_SECS,
            httponly=True,
            secure=env.FLASK_ENV == "production",
            samesite="Strict",
        )

        response.set_cookie(
            "refresh_token",
            new_refresh_token,
            max_age=env.SESSION_EXPIRATION_SECS,
            httponly=True,
            secure=env.FLASK_ENV == "production",
            samesite="Strict",
        )


def remove_session_cookies(response: Response) -> None:
    response.set_cookie(
        "auth_token",
        "",
        expires=0,
        httponly=True,
        secure=(env.FLASK_ENV == "production"),
        samesite="Strict",
    )

    response.set_cookie(
        "refresh_token",
        "",
        expires=0,
        httponly=True,
        secure=(env.FLASK_ENV == "production"),
        samesite="Strict",
    )


def extract_session_tokens_from_request(
    request: Request,
) -> tuple[Optional[str], Optional[str]]:
    auth_token = request.cookies.get("auth_token")
    refresh_token = request.cookies.get("refresh_token")

    return auth_token, refresh_token


def set_current_session_data(auth_token: str) -> None:
    payload_data = decode_jwt(auth_token).data

    g.current_session_id = payload_data.session_id
    g.current_user_id = payload_data.user_data.user_id
    g.current_username = payload_data.user_data.username
    g.current_name = payload_data.user_data.name


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


def signin(username: str, password: str) -> None:
    with db.session.begin():
        user_service.validate_credentials(username, password, for_update=True)
        user = user_service.get_user_by_username_or_raise(username, for_update=True)
        session = create_session(user.id)
        auth_token = create_jwt(session.id, user.id, user.username, user.name)
        set_new_tokens(auth_token, session.refresh_token)


def validate_session(
    *,
    auth_token: str | None = None,
    refresh_token: str | None = None,
) -> None:
    if not auth_token and not refresh_token:
        auth_token, refresh_token = extract_session_tokens_from_request(request)

    if auth_token and is_jwt_valid(auth_token):
        set_current_session_data(auth_token)
        return

    if refresh_token:
        try:
            auth_token, refresh_token = refresh_session(refresh_token=refresh_token)
            set_current_session_data(auth_token)
            set_new_tokens(auth_token, refresh_token)
            return
        except (SessionNotFoundException, SessionExpiredException, IntegrityError):
            pass

    raise UnauthorizedException()


def refresh_session(
    *,
    refresh_token: Optional[str] = None,
    session_id: Optional[UUID] = None,
) -> tuple[str, str]:
    if not refresh_token and not session_id:
        raise ValueError("Either refresh_token or session_id must be provided")

    with db.session.begin():
        query = db.session.query(Session)

        if refresh_token:
            query = query.filter_by(refresh_token=refresh_token)
        else:
            query = query.filter_by(id=session_id)

        session = query.with_for_update().first()

        if not session:
            raise SessionNotFoundException()

        if session.expires_at < datetime.now(timezone.utc):
            with db.session.begin_nested():
                db.session.delete(session)
            raise SessionExpiredException()

        session.refresh_token = Session.generate_refresh_token()
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
