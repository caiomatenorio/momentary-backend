from abc import ABC, abstractmethod
from dataclasses import dataclass

from flask import Response


@dataclass
class ResponseBody(ABC):
    status_code: int
    message: str

    @abstractmethod
    def to_response(self) -> Response:
        pass
