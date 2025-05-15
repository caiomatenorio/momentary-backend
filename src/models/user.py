import uuid
from typing import List
from sqlalchemy import UUID
from ..common.libs.sqlalchemy import db
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(nullable=False)

    username: Mapped[str] = mapped_column(unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    sessions: Mapped[List["Session"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
