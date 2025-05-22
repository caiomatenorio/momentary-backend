from marshmallow import ValidationError

from src.api.response_body.error_response_body import ErrorResponseBody
from src.common.exception.http.http_exception import HttpException
from src.common.exception.http.unauthorized_exception import UnauthorizedException


def handle_http_exception(e: HttpException):
    return ErrorResponseBody(e.status_code, e.message).to_response()


def handle_validation_error(e: ValidationError):
    return ErrorResponseBody(400, "Validation error", e.messages).to_response()


def handle_unauthorized_exception(e: UnauthorizedException):
    return ErrorResponseBody(e.status_code, e.message).to_response(clear_session=True)


def handle_exception(e: Exception):
    return ErrorResponseBody(500, "Internal server error").to_response()
