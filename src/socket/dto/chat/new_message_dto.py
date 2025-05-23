from dataclasses import dataclass
from uuid import UUID

from src.model.message import Message


@dataclass
class NewMessageDto:
    id: str
    sender_id: tuple[str, str]
    content: str

    @staticmethod
    def from_message(message: Message) -> "NewMessageDto":
        return NewMessageDto(
            id=str(message.id),
            sender_id=(str(message.sender_id[0]), str(message.sender_id[1])),
            content=message.content,
        )
