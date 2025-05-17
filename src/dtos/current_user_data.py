from dataclasses import dataclass
from uuid import UUID


@dataclass
class CurrentUserData:
    user_id: UUID
    username: str
    name: str
