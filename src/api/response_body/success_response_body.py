from dataclasses import dataclass
from typing import Any, Optional

from flask import Response, jsonify, make_response

from src.api.response_body.response_body import ResponseBody
from src.service import session_service


@dataclass
class SuccessResponseBody(ResponseBody):
    status_code: int
    message: str
    data: Optional[Any] = None

    def to_response(self, *, clear_session: bool = False) -> Response:
        body = self.__dict__.copy()

        if self.data is None:
            body.pop("data")

        response = make_response(jsonify(body), self.status_code)

        if clear_session:
            session_service.add_clear_session_headers(response)
        else:
            session_service.add_session_headers(response)

        return response
