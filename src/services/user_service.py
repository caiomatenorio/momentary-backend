import bcrypt
from sqlalchemy.exc import IntegrityError

from ..common.exceptions.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from ..common.exceptions.username_already_in_use_exception import (
    UsernameAlreadyInUseException,
)
from ..common.libs.sqlalchemy import db
from ..models.user import User


def user_exists(username: str) -> bool:
    user = User.query.filter_by(username=username).first()
    return user is not None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_user(name: str, username: str, password: str) -> None:
    if user_exists(username):
        raise UsernameAlreadyInUseException()

    try:
        user = User(name=name, username=username, password_hash=hash_password(password))
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise UsernameAlreadyInUseException()
    except Exception as e:
        db.session.rollback()
        raise e


def validate_credentials(username: str, password: str) -> None:
    user = User.query.filter_by(username=username).first()
    are_valid = check_password(password, user.password_hash) if user else False

    if not are_valid:
        raise InvalidCredentialsException()


def get_user_by_username(username: str) -> User | None:
    user = User.query.filter_by(username=username).first()
    return user


def get_user_by_username_or_raise(username: str) -> User:
    user = get_user_by_username(username)
    if not user:
        raise InvalidCredentialsException()
    return user
