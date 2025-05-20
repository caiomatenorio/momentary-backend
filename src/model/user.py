from typing import List
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.singleton.db import db


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(nullable=False)

    username: Mapped[str] = mapped_column(unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    sessions: Mapped[List["Session"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )

    chat_participations: Mapped[List["ChatParticipant"]] = relationship(  # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
