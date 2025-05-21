from typing import List, Optional
from uuid import UUID

from src.common.exception.http.direct_chat_already_exists_exception import (
    DirectChatAlreadyExistsException,
)
from src.model.chat import Chat
from src.model.chat_participant import ChatParticipant
from src.service import user_service
from src.singleton.db import db


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


def get_all_current_user_chats() -> List[Chat]:
    current_user_id = user_service.get_current_user().user_id
    chats = (
        db.session.query(Chat)
        .join(ChatParticipant)
        .filter(ChatParticipant.user_id == current_user_id)
        .all()
    )
    return chats
