from flask import g, request

from ..libs.redis import redis
from ..services import session_service


def store_socket_session_data() -> None:
    session_data = session_service.get_current_session_data()
    database = f"socket_session:{request.sid}"
    redis.hmset(database, session_data)


def get_socket_session_data_by_sid() -> dict | None:
    database = f"socket_session:{request.sid}"
    user_data = redis.hgetall(database)

    if not user_data:
        return

    return {
        "session_id": user_data.get("session_id"),
        "user_id": user_data.get("user_id"),
        "user_name": user_data.get("user_name"),
        "user_username": user_data.get("user_username"),
    }


def delete_socket_session_data_by_sid() -> None:
    database = f"socket_session:{request.sid}"
    redis.delete(database)
