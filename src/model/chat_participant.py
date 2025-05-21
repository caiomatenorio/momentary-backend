from typing import List, Tuple
from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.singleton.db import db


class ChatParticipant(db.Model):
    __tablename__ = "chat_participants"
    __table_args__ = (PrimaryKeyConstraint("chat_id", "user_id"),)

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

    @hybrid_property
    def id(self) -> Tuple[UUID, UUID]:  # type: ignore
        return self.chat_id, self.user_id

    @id.expression
    def id(cls):
        return tuple_(cls.chat_id, cls.user_id)  # type: ignore

    def __repr__(self) -> str:
        return f"<ChatParticipant {self.user_id} in chat {self.chat_id}>"
