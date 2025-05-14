from .utils.exceptions.http_exception import HttpException
from flask import jsonify
from ..main import app
from marshmallow import ValidationError

@app.errorhandler(HttpException)
def handle_http_exception(e: HttpException):
    response = {
        "status_code": e.status_code, 
        "message": e.message
    }

    return jsonify(response), e.status_code


@app.errorhandler(ValidationError)
def handle_validation_error(e: ValidationError):
    response = {
        "status_code": 400,
        "message": "Validation error",
        "errors": e.messages
    }

    return jsonify(response), 400