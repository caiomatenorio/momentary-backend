from dataclasses import dataclass
from typing import Optional
from .response_body import ResponseBody
from flask import Response, jsonify

@dataclass
class ErrorResponseBody(ResponseBody):
    status_code: int
    message: str
    errors: Optional[list[str] | list | dict] = None

    def to_response(self) -> tuple[Response, int]:
        body = self.__dict__.copy()

        if self.errors is None:
            body.pop("errors")
        
        return jsonify(body), self.status_code