from ..models.user import User
from ..common.exceptions.username_already_in_use_exception import UsernameAlreadyInUseException
from sqlalchemy.exc import IntegrityError
from ..common.libs.sqlalchemy import db

def user_exists(username: str) -> bool:
    user = User.query.filter_by(username=username).first()
    return user is not None

def create_user(name: str, username: str, password: str):
    if user_exists(username):
        raise UsernameAlreadyInUseException()
    
    try:
        user = User(name=name, username=username, password=password)
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise UsernameAlreadyInUseException()
    except Exception as e:
        db.session.rollback()
        raise e