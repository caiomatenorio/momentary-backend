from dataclasses import dataclass
from typing import List, Tuple
from uuid import UUID

from src.model.chat import Chat


@dataclass
class _User:
    id: UUID
    name: str
    username: str


@dataclass
class _ChatParticipant:
    id: Tuple[UUID, UUID]
    user: _User


@dataclass
class _Message:
    id: UUID
    sender_id: Tuple[UUID, UUID]
    content: str


@dataclass
class GetChatResponseDto:
    id: UUID
    participants: List[_ChatParticipant]
    messages: List[_Message]

    @staticmethod
    def from_chat(chat: Chat) -> "GetChatResponseDto":
        participants = [
            _ChatParticipant(
                id=chat_participant.id,
                user=_User(
                    id=chat_participant.user.id,
                    name=chat_participant.user.name,
                    username=chat_participant.user.username,
                ),
            )
            for chat_participant in chat.participants
        ]

        messages = [
            _Message(
                id=message.id,
                sender_id=message.sender_id,
                content=message.content,
            )
            for message in chat.messages
        ]

        return GetChatResponseDto(
            id=chat.id,
            participants=participants,
            messages=messages,
        )
