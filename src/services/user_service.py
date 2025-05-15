import bcrypt
from flask import g
from sqlalchemy.exc import IntegrityError

from ..exceptions.http_exceptions.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from ..exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from ..exceptions.http_exceptions.user_not_found_exception import UserNotFoundException
from ..exceptions.http_exceptions.username_already_in_use_exception import (
    UsernameAlreadyInUseException,
)
from ..libs.sqlalchemy import db
from ..models.user import User
from . import session_service


def user_exists(username: str, *, for_update: bool = False) -> bool:
    query = User.query.filter_by(username=username)

    if for_update:
        query = query.with_for_update()

    user = query.first()
    return user is not None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_user(name: str, username: str, password: str) -> None:
    with db.session.begin():
        if user_exists(username, for_update=True):
            raise UsernameAlreadyInUseException()

        user = User(name=name, username=username, password_hash=hash_password(password))
        db.session.add(user)


def validate_credentials(
    username: str, password: str, *, for_update: bool = False
) -> None:
    user = get_user_by_username_or_raise(username, for_update=for_update)
    are_valid = check_password(password, user.password_hash) if user else False

    if not are_valid:
        raise InvalidCredentialsException()


def get_user_by_username(username: str, *, for_update: bool = False) -> User | None:
    query = User.query.filter_by(username=username)

    if for_update:
        query = query.with_for_update()

    user = query.first()
    return user


def get_user_by_username_or_raise(username: str, *, for_update: bool = False) -> User:
    user = get_user_by_username(username, for_update=for_update)
    if not user:
        raise UserNotFoundException()
    return user


def get_user_by_id(user_id: int, *, for_update: bool = False) -> User | None:
    query = User.query.filter_by(id=user_id)

    if for_update:
        query = query.for_update()

    user = query.first()
    return user


def get_user_by_id_or_raise(user_id: int, *, for_update: bool = False) -> User:
    user = get_user_by_id(user_id, for_update=for_update)
    if not user:
        raise UserNotFoundException()
    return user


def whoami() -> dict:
    current_user_data = {
        "user_id": g.get("current_user_id"),
        "username": g.get("current_username"),
        "name": g.get("current_name"),
    }

    return current_user_data


def change_name(new_name: str) -> None:
    with db.session.begin():
        if user_exists(new_name, for_update=True):
            raise UsernameAlreadyInUseException()

        user_id = g.get("current_user_id")
        user = get_user_by_id_or_raise(user_id, for_update=True)
        user.name = new_name
        db.session.add(user)
