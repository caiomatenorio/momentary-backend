from flask import request

from ..blueprints.api import api
from ..decorators.requires_authentication import requires_authentication
from ..dtos.success_response_body import SuccessResponseBody
from ..schemas.signin_schema import SigninSchema
from ..services import session_service


@api.post("/signin")
def signin():
    body = SigninSchema().load(request.json)
    session_service.sign_in(body.get("username"), body.get("password"))
    return SuccessResponseBody(200, "User signed in successfully").to_response()
