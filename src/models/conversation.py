from typing import List
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..libs.sqlalchemy import db
from .enums.conversation_type import ConversationType


class DirectConversation(db.Model):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )

    type: Mapped[ConversationType] = mapped_column(
        Enum(ConversationType), nullable=False
    )

    participants: Mapped[List["ConversationParticipant"]] = relationship(  # type: ignore
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    messages: Mapped[List["Message"]] = relationship(  # type: ignore
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.id}>"
