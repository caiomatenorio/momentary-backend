from dataclasses import dataclass
from uuid import UUID

from src.dtos.user_data import UserData


@dataclass
class SessionData:
    session_id: UUID
    user_data: UserData

    def to_dict(self) -> dict:
        return {
            "session_id": str(self.session_id),
            "user_data": self.user_data.to_dict(),
        }

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
            user_data=UserData.from_dict(data["user_data"]),
        )

    @staticmethod
    def from_flattened(flattened: dict[str, str]) -> "SessionData":
        return SessionData(
            session_id=UUID(flattened["session_id"]),
            user_data=UserData.from_dict(
                {
                    "user_id": flattened["user_id"],
                    "username": flattened["username"],
                    "name": flattened["name"],
                }
            ),
        )
