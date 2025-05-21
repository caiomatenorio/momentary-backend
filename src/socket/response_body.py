from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ResponseBody:
    message: str
    data: Optional[Any] = None

    def to_dict(self) -> dict:
        result = self.__dict__

        if self.data is None:
            result.pop("data")

        if hasattr(self.data, "__dict__"):
            result["data"] = self.data.__dict__

        return result
