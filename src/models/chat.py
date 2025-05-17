from typing import List
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..libs.sqlalchemy import db
from .enums.conversation_type import ChatType


class Chat(db.Model):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )

    type: Mapped[ChatType] = mapped_column(Enum(ChatType), nullable=False)

    participants: Mapped[List["ChatParticipant"]] = relationship(  # type: ignore
        back_populates="chat",
        cascade="all, delete-orphan",
    )

    messages: Mapped[List["Message"]] = relationship(  # type: ignore
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Chat {self.id} ({self.type})>"
