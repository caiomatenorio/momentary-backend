from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..env import env
from ..libs.sqlalchemy import db


class Message(db.Model):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
    )

    conversation: Mapped["DirectConversation"] = relationship(  # type: ignore
        back_populates="messages",
    )

    sender_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation_participants.id"), nullable=False
    )

    sender: Mapped["ConversationParticipant"] = relationship(  # type: ignore
        back_populates="messages",
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

    @staticmethod
    def calculate_expiration() -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=env.MESSAGE_TTL_SECS)

    def __repr__(self) -> str:
        return f"<Message {self.id}>"
