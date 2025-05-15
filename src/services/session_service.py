from datetime import datetime, timedelta, timezone

import jwt
from flask import Request, Response
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
    db.session.commit()
    return session


def create_jwt(session_id: str, username: str, name: str) -> str:
    jwt_expiration_secs = env.JWT_EXPIRATION_SECS

    payload = {
        "data": {
            "session_id": session_id,
            "username": username,
            "name": name,
        },
        "exp": datetime.now(timezone.utc) + timedelta(seconds=jwt_expiration_secs),
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, env.JWT_SECRET_KEY, algorithm="HS256")


def decode_jwt(jwt: str) -> dict:
    try:
        payload = jwt.decode(jwt, env.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")  # TODO: create a custom exception
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")  # TODO: create a custom exception


def is_jwt_valid(jwt: str) -> bool:
    try:
        payload = decode_jwt(jwt)
        session_id = payload["data"]["session_id"]
        session = db.session.query(Session).filter_by(id=session_id).first()

        if not session:
            return False

        if session.expires_at < datetime.now(timezone.utc):
            return False

        return True
    except ValueError:
        return False


def add_session_cookies(
    response: Response, auth_token: str, referesh_token: str
) -> None:
    response.set_cookie(
        "auth_token",
        auth_token,
        max_age=env.JWT_EXPIRATION_SECS,
        httponly=True,
        secure=env.ENV == "production",
        samesite="Strict",
    )

    response.set_cookie(
        "refresh_token",
        referesh_token,
        max_age=env.SESSION_EXPIRATION_SECS,
        httponly=True,
        secure=env.ENV == "production",
        samesite="Strict",
    )


def remove_session_cookies(response: Response) -> None:
    response.delete_cookie("auth_token")
    response.delete_cookie("refresh_token")


def extract_session_tokens_from_request(
    request: Request,
) -> tuple[str | None, str | None]:
    auth_token = request.cookies.get("auth_token")
    refresh_token = request.cookies.get("refresh_token")

    return auth_token, refresh_token


def sign_in(username: str, password: str, response: Response) -> None:
    user_service.validate_credentials(username, password)
    user = user_service.get_user_by_username_or_raise(username)
    session = create_session(user)
    jwt = create_jwt(session.id, user.username, user.name)
    add_session_cookies(response, jwt, session.refresh_token)


def refresh_session(refresh_token: str) -> tuple[str, str]:
    session = db.session.query(Session).filter_by(refresh_token=refresh_token).first()

    if not session:
        raise SessionNotFoundException()

    if session.expires_at < datetime.now(timezone.utc):
        db.session.delete(session)
        db.session.commit()
        raise SessionExpiredException()

    try:
        session.refresh_token = Session.generate_refresh_token()
        session.expires_at = Session.calculate_expiration()
        session.updated_at = datetime.now(timezone.utc)
        db.session.add(session)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    else:
        user = user_service.get_user_by_id_or_raise(session.user_id)
        jwt = create_jwt(session.id, user.username, user.name)

        return jwt, session.refresh_token


def validate_session(request: Request) -> tuple[str, str] | None:
    auth_token, refresh_token = extract_session_tokens_from_request(request)

    if auth_token and is_jwt_valid(auth_token):
        return

    if refresh_token:
        try:
            new_auth_token, new_refresh_token = refresh_session(refresh_token)
            return new_auth_token, new_refresh_token
        except SessionNotFoundException | SessionExpiredException | IntegrityError:
            pass

    raise UnauthorizedException()
