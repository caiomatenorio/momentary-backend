from .common.exceptions.http_exception import HttpException
from marshmallow import ValidationError
from .dtos.error_response_body import ErrorResponseBody


def handle_http_exception(e: HttpException):
    return ErrorResponseBody(e.status_code, e.message).to_response()


def handle_validation_error(e: ValidationError):
    return ErrorResponseBody(400, "Validation error", e.messages).to_response()
