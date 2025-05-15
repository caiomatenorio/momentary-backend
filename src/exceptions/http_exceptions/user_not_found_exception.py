from .http_exception import HttpException


class UserNotFoundException(HttpException):
    status_code = 404
    message = "User not found."
