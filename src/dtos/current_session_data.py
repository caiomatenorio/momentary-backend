from dataclasses import dataclass
from uuid import UUID

from flask.ctx import _AppCtxGlobals

from src.dtos.current_user_data import CurrentUserData


@dataclass
class CurrentSessionData:
    session_id: UUID
    current_user_data: CurrentUserData

    def flatten(self) -> dict[str, str]:
        return {
            "session_id": str(self.session_id),
            "user_id": str(self.current_user_data.user_id),
            "username": self.current_user_data.username,
            "name": self.current_user_data.name,
        }

    @staticmethod
    def from_flattened(flattened: dict[str, str]) -> "CurrentSessionData":
        return CurrentSessionData(
            session_id=UUID(flattened["session_id"]),
            current_user_data=CurrentUserData(
                user_id=UUID(flattened["user_id"]),
                username=flattened["username"],
                name=flattened["name"],
            ),
        )
