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

    def to_response(
        self, *, remove_session_cookies: bool = False
    ) -> tuple[Response, int]:
        body = self.__dict__.copy()

        if self.errors is None:
            body.pop("errors")

        response = make_response(jsonify(body), self.status_code)

        if remove_session_cookies:
            session_service.remove_session_cookies(response)

        return response
