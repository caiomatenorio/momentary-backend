from .http_exception import HttpException


class UnauthorizedException(HttpException):
    status_code = 401
    message = "The user is not authorized to perform this action."
