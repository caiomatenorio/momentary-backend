from dataclasses import dataclass
from typing import Optional

from flask import Response, jsonify, make_response

from ..services import session_service
from .response_body import ResponseBody


@dataclass
class ErrorResponseBody(ResponseBody):
    status_code: int
    message: str
    errors: Optional[list[str] | list | dict] = None

    def to_response(self, *, clear_session: bool = False) -> Response:
        body = self.__dict__.copy()

        if self.errors is None:
            body.pop("errors")

        response = make_response(jsonify(body), self.status_code)

        if clear_session:
            session_service.add_clear_session_headers(response)

        return response
