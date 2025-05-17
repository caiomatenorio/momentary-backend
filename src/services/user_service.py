from uuid import UUID

import bcrypt
from flask import g
from sqlalchemy.exc import IntegrityError

from src.dtos.user_data import UserData

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

        user = User(name=name, username=username, password_hash=hash_password(password))  # type: ignore
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


def get_user_by_id(user_id: UUID, *, for_update: bool = False) -> User | None:
    query = db.session.query(User).filter_by(id=user_id)

    if for_update:
        query = query.with_for_update()

    user = query.first()
    return user


def get_user_by_id_or_raise(user_id: UUID, *, for_update: bool = False) -> User:
    user = get_user_by_id(user_id, for_update=for_update)
    if not user:
        raise UserNotFoundException()
    return user


def whoami() -> UserData:
    current_session_data = session_service.get_current_session_data()
    current_user_data = current_session_data.user_data
    return current_user_data


def update_name(new_name: str) -> None:
    with db.session.begin():
        user_id = whoami().user_id
        user = get_user_by_id_or_raise(user_id, for_update=True)
        user.name = new_name
        db.session.add(user)


def update_username(new_username: str) -> None:
    with db.session.begin():
        if user_exists(new_username, for_update=True):
            raise UsernameAlreadyInUseException()

        user_id = whoami().user_id
        user = get_user_by_id_or_raise(user_id, for_update=True)
        user.username = new_username
        db.session.add(user)


def update_password(old_password: str, new_password: str) -> None:
    with db.session.begin():
        user_id = whoami().user_id
        user = get_user_by_id_or_raise(user_id, for_update=True)

        if not check_password(old_password, user.password_hash):
            raise InvalidCredentialsException()

        new_password_hash = hash_password(new_password)
        user.password_hash = new_password_hash
        db.session.add(user)
