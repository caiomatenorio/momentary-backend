import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..config import get_env_var
from ..common.libs.sqlalchemy import db

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

    user: Mapped["User"] = relationship(back_populates="sessions")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
        + timedelta(seconds=int(get_env_var("SESSION_DURATION_SECS"))),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Session {self.id}>"