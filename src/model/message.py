from datetime import datetime, timedelta, timezone
from typing import Tuple
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.singleton.db import db
from src.singleton.env import env


class Message(db.Model):
    __tablename__ = "messages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sender_chat_id", "sender_user_id"],
            ["chat_participants.chat_id", "chat_participants.user_id"],
        ),
    )

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
        back_populates="messages",
    )

    sender_user_id: Mapped[UUID] = mapped_column()

    sender_chat_id: Mapped[UUID] = mapped_column()

    sender: Mapped["ChatParticipant"] = relationship(  # type: ignore
        back_populates="messages",
        primaryjoin="and_(Message.sender_chat_id==ChatParticipant.chat_id, Message.sender_user_id==ChatParticipant.user_id)",
    )

    content: Mapped[str] = mapped_column(nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: Message.calculate_expiration(),
        nullable=False,
    )

    @hybrid_property
    def sender_id(self) -> Tuple[UUID, UUID]:  # type: ignore
        return self.sender_chat_id, self.sender_user_id

    @sender_id.expression
    def sender_id(cls):
        return tuple_(cls.sender_chat_id, cls.sender_user_id)  # type: ignore

    @staticmethod
    def calculate_expiration() -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=env.MESSAGE_TTL_SECS)

    def __repr__(self) -> str:
        return f"<Message {self.id}>"
