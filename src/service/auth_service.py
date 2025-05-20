from src.service import session_service, user_service
from src.singleton.db import db


def signup(username: str, password: str, name: str) -> None:
    user_service.create_user(
        name=name,
        username=username,
        password=password,
    )


def signin(username: str, password: str) -> None:
    with db.session.begin():
        user_service.validate_credentials(username, password, for_update=True)
        user = user_service.get_user_by_username_or_raise(username, for_update=True)
        session = session_service.create_session(user.id)
        auth_token = session_service.create_jwt(
            session.id,
            user.id,
            user.username,
            user.name,
        )
        session_service.set_new_tokens(auth_token, session.refresh_token)


def signout() -> None:
    session_service.delete_current_session()
