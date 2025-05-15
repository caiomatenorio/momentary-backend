from dataclasses import dataclass
from typing import Optional

from flask import Response, jsonify, make_response

from ..services import session_service
from .response_body import ResponseBody


@dataclass
class SuccessResponseBody(ResponseBody):
    status_code: int
    message: str
    data: Optional[any] = None

    def to_response(self) -> tuple[Response, int]:
        body = self.__dict__.copy()

        if self.data is None:
            body.pop("data")

        response = make_response(jsonify(body), self.status_code)
        session_service.add_session_cookies(response)

        return response
