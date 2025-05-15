import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..common.libs.sqlalchemy import db
from ..env import env


class Session(db.Model):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
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
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )

    @staticmethod
    def calculate_expiration() -> datetime:
        expiration_time = env["SESSION_EXPIRATION_SECS"]
        return datetime.now(timezone.utc) + timedelta(seconds=expiration_time)

    def __repr__(self) -> str:
        return f"<Session {self.id}>"
