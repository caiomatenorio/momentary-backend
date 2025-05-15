import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..env import env
from ..libs.sqlalchemy import db


class Session(db.Model):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=lambda: uuid4(),
        unique=True,
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="sessions")  # type: ignore

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: Session.calculate_expiration(),
        nullable=False,
    )

    refresh_token: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        default=lambda: Session.generate_refresh_token(),
        unique=True,
        nullable=False,
    )

    @staticmethod
    def calculate_expiration() -> datetime:
        expiration_time = env.SESSION_EXPIRATION_SECS
        return datetime.now(timezone.utc) + timedelta(seconds=expiration_time)

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)

    def __repr__(self) -> str:
        return f"<Session {self.id}>"
