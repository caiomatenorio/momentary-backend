from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserData:
    user_id: UUID
    username: str
    name: str

    def to_dict(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "username": self.username,
            "name": self.name,
        }

    @staticmethod
    def from_dict(data: dict) -> "UserData":
        return UserData(
            user_id=UUID(data["user_id"]),
            username=data["username"],
            name=data["name"],
        )
