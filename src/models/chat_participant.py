from typing import List
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..libs.sqlalchemy import db


class ChatParticipant(db.Model):
    __tablename__ = "chat_participants"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )

    chat_id: Mapped[UUID] = mapped_column(
        ForeignKey("chats.id"),
        nullable=False,
    )

    chat: Mapped["Chat"] = relationship(  # type: ignore
        back_populates="participants",
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_participations")  # type: ignore

    messages: Mapped[List["Message"]] = relationship(  # type: ignore
        back_populates="sender",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ChatParticipant {self.id}>"
