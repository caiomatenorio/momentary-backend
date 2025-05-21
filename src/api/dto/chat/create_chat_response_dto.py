from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateChatResponseDto:
    id: UUID
