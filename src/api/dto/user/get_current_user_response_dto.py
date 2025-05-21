from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetCurrentUserResponseDto:
    id: UUID
    name: str
    username: str
