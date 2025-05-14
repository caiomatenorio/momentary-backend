from .http_exception import HttpException

class UsernameAlreadyInUseException(HttpException):
    status_code = 409
    message = "Username already in use."