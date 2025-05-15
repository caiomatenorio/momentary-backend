from marshmallow import ValidationError

from .dtos.error_response_body import ErrorResponseBody
from .exceptions.http_exceptions.http_exception import HttpException
from .exceptions.http_exceptions.unauthorized_exception import UnauthorizedException
from .services.session_service import remove_session_cookies


def handle_http_exception(e: HttpException):
    return ErrorResponseBody(e.status_code, e.message).to_response()


def handle_validation_error(e: ValidationError):
    return ErrorResponseBody(400, "Validation error", e.messages).to_response()


def handle_unauthorized_exception(e: UnauthorizedException):
    return ErrorResponseBody(e.status_code, e.message).to_response(
        remove_session_cookies=True
    )
