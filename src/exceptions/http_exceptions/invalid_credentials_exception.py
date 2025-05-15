from .http_exception import HttpException


class InvalidCredentialsException(HttpException):
    status_code = 401
    message = "Invalid credentials."
