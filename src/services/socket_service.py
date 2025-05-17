import asyncio
from collections.abc import Awaitable
from typing import Optional

from flask import request

from ..dtos.session_data import SessionData
from ..libs.redis import redis
from ..services import session_service


def store_socket_session_data() -> None:
    session_data = session_service.get_current_session_data()
    db_key = f"socket_session:{request.sid}"  # type: ignore
    redis.hset(db_key, mapping=session_data.flatten())


async def get_socket_session_data_by_sid() -> Optional[SessionData]:
    db_key = f"socket_session:{request.sid}"  # type: ignore
    query = redis.hgetall(db_key)
    flattened_session_data = (
        await query
        if asyncio.iscoroutine(query) or isinstance(query, Awaitable)
        else query
    )

    if not flattened_session_data:
        return

    return SessionData.from_flattened(flattened_session_data)


def delete_socket_session_data_by_sid() -> None:
    db_key = f"socket_session:{request.sid}"  # type: ignore
    redis.delete(db_key)
