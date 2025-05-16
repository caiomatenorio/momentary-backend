from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from flask import Request, Response, g, request
from sqlalchemy.exc import IntegrityError

from ..env import env
from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..exceptions.session_expired_exception import SessionExpiredException
from ..exceptions.session_not_found_exception import SessionNotFoundException
from ..libs.sqlalchemy import db
from ..models.session import Session
from ..models.user import User
from . import user_service


def create_session(user: User) -> Session:
    session = Session(user=user)
    db.session.add(session)
    return session


def create_jwt(session_id: UUID, user_id: UUID, username: str, name: str) -> str:
    jwt_expiration_secs = env.JWT_EXPIRATION_SECS

    payload = {
        "data": {
            "session_id": str(session_id),
            "user_id": str(user_id),
            "username": username,
            "name": name,
        },
        "exp": datetime.now(timezone.utc) + timedelta(seconds=jwt_expiration_secs),
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, env.JWT_SECRET_KEY, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, env.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")  # TODO: create a custom exception
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")  # TODO: create a custom exception


def is_jwt_valid(jwt: str) -> bool:
    try:
        decode_jwt(jwt)
        return True
    except ValueError:
        return False


def get_new_tokens() -> tuple[str | None, str | None]:
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
            secure=env.ENV == "production",
            samesite="Strict",
        )

        response.set_cookie(
            "refresh_token",
            new_refresh_token,
            max_age=env.SESSION_EXPIRATION_SECS,
            httponly=True,
            secure=env.ENV == "production",
            samesite="Strict",
        )


def remove_session_cookies(response: Response) -> None:
    response.set_cookie(
        "auth_token",
        "",
        expires=0,
        httponly=True,
        secure=env.ENV == "production",
        samesite="Strict",
    )

    response.set_cookie(
        "refresh_token",
        "",
        expires=0,
        httponly=True,
        secure=env.ENV == "production",
        samesite="Strict",
    )


def extract_session_tokens_from_request(
    request: Request,
) -> tuple[str | None, str | None]:
    auth_token = request.cookies.get("auth_token")
    refresh_token = request.cookies.get("refresh_token")

    return auth_token, refresh_token


def set_current_session_data(auth_token) -> None:
    payload_data = decode_jwt(auth_token)["data"]
    g.current_session_id = payload_data["session_id"]
    g.current_user_id = payload_data["user_id"]
    g.current_username = payload_data["username"]
    g.current_name = payload_data["name"]


def get_current_session_data() -> dict:
    return {
        "session_id": g.get("current_session_id"),
        "user_id": g.get("current_user_id"),
        "username": g.get("current_username"),
        "name": g.get("current_name"),
    }


def get_session_by_id(session_id: UUID, *, for_update: bool = False) -> Session | None:
    query = db.session.query(Session).filter_by(id=session_id)

    if for_update:
        query = query.with_for_update()

    session = query.first()
    return session


def get_session_by_id_or_raise(
    session_id: UUID, *, for_update: bool = False
) -> Session:
    session = get_session_by_id(session_id, for_update=for_update)

    if not session:
        raise SessionNotFoundException()

    return session


def signin(username: str, password: str) -> None:
    with db.session.begin():
        user_service.validate_credentials(username, password)
        user = user_service.get_user_by_username_or_raise(username)
        session = create_session(user)
        auth_token = create_jwt(session.id, user.id, user.username, user.name)

        g.new_auth_token = auth_token
        g.new_refresh_token = session.refresh_token


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
            g.new_auth_token, g.new_refresh_token = refresh_session(
                refresh_token=refresh_token
            )
            set_current_session_data(g.new_auth_token)
            return
        except (SessionNotFoundException, SessionExpiredException, IntegrityError):
            pass

    raise UnauthorizedException()


def refresh_session(
    *,
    refresh_token: str = None,
    session_id: UUID = None,
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
        session_id = get_current_session_data().get("session_id")
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
