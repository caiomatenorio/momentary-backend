from dataclasses import dataclass
from typing import Optional
from .response_body import ResponseBody
from flask import Response, jsonify


@dataclass
class SuccessResponseBody(ResponseBody):
    status_code: int
    message: str
    data: Optional[any] = None

    def to_response(self) -> tuple[Response, int]:
        body = self.__dict__.copy()

        if self.data is None:
            body.pop("data")

        return jsonify(body), self.status_code
