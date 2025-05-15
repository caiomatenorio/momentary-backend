from flask import make_response, request

from ..common.blueprints.api import api
from ..dtos.success_response_body import SuccessResponseBody
from ..schemas.signin_schema import SigninSchema
from ..services import session_service


@api.post("/signin")
def signin():
    body = SigninSchema().load(request.json)
    response = make_response(
        *SuccessResponseBody(200, "User signed in successfully").to_response()
    )
    session_service.sign_in(body.get("username"), body.get("password"), response)
    return response
