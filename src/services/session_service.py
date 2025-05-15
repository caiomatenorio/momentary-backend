from datetime import datetime, timedelta, timezone

import jwt
from flask import Response

from ..common.libs.sqlalchemy import db
from ..env import env
from ..models.session import Session
from ..models.user import User
from . import user_service


def create_session(user: User) -> Session:
    session = Session(user=user)
    db.session.add(session)
    db.session.commit()
    return session


def create_jwt(session_id: str, username: str, name: str) -> str:
    payload = {
        "data": {
            "session_id": session_id,
            "username": username,
            "name": name,
        },
        "exp": env["JWT_EXPIRATION_SECS"],
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, env["JWT_SECRET_KEY"], algorithm="HS256")


def decode_jwt(jwt: str) -> dict:
    try:
        payload = jwt.decode(jwt, env["JWT_SECRET"], algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")  # TODO: create a custom exception
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")  # TODO: create a custom exception


def add_session_cookies(
    response: Response, auth_token: str, referesh_token: str
) -> None:
    response.set_cookie(
        "auth_token",
        auth_token,
        max_age=env["JWT_EXPIRATION_SECS"],
        httponly=True,
        secure=env["ENV"] == "production",
        samesite="Strict",
    )

    response.set_cookie(
        "refresh_token",
        referesh_token,
        max_age=env["SESSION_EXPIRATION_SECS"],
        httponly=True,
        secure=env["ENV"] == "production",
        samesite="Strict",
    )


def sign_in(username: str, password: str, response: Response) -> None:
    user_service.validate_credentials(username, password)
    user = user_service.get_user_by_username_or_raise(username)
    session = create_session(user)
    jwt = create_jwt(session.id, user.username, user.name)
    add_session_cookies(response, jwt, session.refresh_token)
