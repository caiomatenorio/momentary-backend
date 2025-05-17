from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserData:
    user_id: UUID
    username: str
    name: str
