from dataclasses import dataclass
from uuid import UUID

from src.dtos.user_data import UserData


@dataclass
class SessionData:
    session_id: UUID
    user_data: UserData

    def flatten(self) -> dict[str, str]:
        return {
            "session_id": str(self.session_id),
            "user_id": str(self.user_data.user_id),
            "username": self.user_data.username,
            "name": self.user_data.name,
        }

    @staticmethod
    def from_dict(data: dict) -> "SessionData":
        return SessionData(
            session_id=UUID(data["session_id"]),
            user_data=UserData(
                user_id=UUID(data["user_id"]),
                username=data["username"],
                name=data["name"],
            ),
        )

    @staticmethod
    def from_flattened(flattened: dict[str, str]) -> "SessionData":
        return SessionData(
            session_id=UUID(flattened["session_id"]),
            user_data=UserData(
                user_id=UUID(flattened["user_id"]),
                username=flattened["username"],
                name=flattened["name"],
            ),
        )
