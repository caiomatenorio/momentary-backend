from typing import List, Optional
from uuid import UUID

from flask_socketio import emit
from sqlalchemy import func

from src.common.exception.http.chat_not_found_exception import ChatNotFoundException
from src.common.exception.http.direct_chat_already_exists_exception import (
    DirectChatAlreadyExistsException,
)
from src.model.chat import Chat
from src.model.chat_participant import ChatParticipant
from src.model.message import Message
from src.service import socket_service, user_service
from src.singleton.db import db
from src.socket.response_body import ResponseBody


def get_direct_chat_by_participants(user_ids: set[UUID]) -> Optional[Chat]:
    if len(user_ids) != 2:
        return

    # TODO: Update query when implement group chats, because it consideres every chat with 2
    # participants as a direct chat

    # Get a direct chat by its participant user ids
    chat = (
        db.session.query(Chat)  # Query chats
        .join(ChatParticipant)  # Join with chat participants
        .filter(ChatParticipant.user_id.in_(user_ids))  # Filter by user IDs
        .having(
            db.func.count(ChatParticipant.user_id) == 2
        )  # Ensure exactly two participants
        .group_by(Chat.id)  # Group by chat ID
        .first()  # Get the first result (unique possibility or None)
    )
    return chat


def create_direct_chat(contact_username: str) -> UUID:
    with db.session.begin():
        # Query the current user and contact user to create a for update lock on them
        current_user = user_service.get_user_by_id_or_raise(
            user_service.get_current_user().user_id,
            for_update=True,
        )
        contact_user = user_service.get_user_by_username_or_raise(
            contact_username,
            for_update=True,
        )

        if get_direct_chat_by_participants({current_user.id, contact_user.id}):
            raise DirectChatAlreadyExistsException()

        chat = Chat(
            participants=[  # type: ignore
                ChatParticipant(user=current_user),  # type: ignore
                ChatParticipant(user=contact_user),  # type: ignore
            ]
        )

        db.session.add(chat)

    return chat.id


def get_all_chats(*, for_socket: bool = False) -> List[Chat]:
    if for_socket:
        current_user_id = socket_service.get_socket_session_or_raise().user_data.user_id
    else:
        current_user_id = user_service.get_current_user().user_id

    chats = (
        db.session.query(Chat)
        .join(ChatParticipant)
        .filter(ChatParticipant.user_id == current_user_id)
        .all()
    )

    return chats


def get_chat_by_id(
    chat_id: UUID,
    *,
    for_update: bool = False,
    for_socket: bool = False,
) -> Optional[Chat]:
    if for_socket:
        current_user_id = socket_service.get_socket_session_or_raise().user_data.user_id
    else:
        current_user_id = user_service.get_current_user().user_id

    query = (
        db.session.query(Chat)
        .join(ChatParticipant)
        .filter(ChatParticipant.user_id == current_user_id, Chat.id == chat_id)
    )

    if for_update:
        query = query.with_for_update()

    chat = query.first()
    return chat


def get_chat_by_id_or_raise(
    chat_id: UUID,
    *,
    for_update: bool = False,
    for_socket: bool = False,
) -> Chat:
    chat = get_chat_by_id(
        chat_id,
        for_update=for_update,
        for_socket=for_socket,
    )

    if chat is None:
        raise ChatNotFoundException()
    return chat


def connect_to_chat(chat: Chat) -> None:
    socket_service.connect_to_room(str(chat.id))


def connect_to_all_chats() -> None:
    chats = get_all_chats(for_socket=True)

    for chat in chats:
        connect_to_chat(chat)


def send_message(chat_id: UUID, content: str) -> Message:
    with db.session.begin():
        user_id = socket_service.get_socket_session_or_raise().user_data.user_id
        # Validate chat existence and create a for update lock on it
        get_chat_by_id_or_raise(chat_id, for_update=True, for_socket=True)
        message = Message(
            chat_id=chat_id,  # type: ignore
            sender_chat_id=chat_id,  # type: ignore
            sender_user_id=user_id,  # type: ignore
            content=content,  # type: ignore
        )
        db.session.add(message)

    return message


def clean_expired_messages() -> None:
    with db.session.begin():
        expired_messages = (
            db.session.query(Message)
            .filter(Message.expires_at < db.func.now())
            .with_for_update()
            .all()
        )

        for message in expired_messages:
            db.session.delete(message)

    for message in expired_messages:
        emit(
            "message_expired",
            ResponseBody(
                "Message expired.",
                {"id": str(message.id)},
            ).to_dict(),
            to=str(message.chat_id),
        )


def clean_empty_chats() -> None:
    with db.session.begin():
        empty_chats = (
            db.session.query(Chat)
            .outerjoin(Chat.messages)
            .group_by(Chat.id)
            .having(func.count(Message.id) == 0)
            .all()
        )

        for empty_chat in empty_chats:
            emit(
                "chat_deleted",
                ResponseBody(
                    "Deleting chat due to inactivity.",
                    {"id": str(empty_chat.id)},
                ).to_dict(),
                to=str(empty_chat.id),
            )
            db.session.delete(empty_chat)
