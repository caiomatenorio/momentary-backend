from flask import request

from ..blueprints.api import api
from ..decorators.requires_rest_authentication import requires_rest_authentication
from ..dtos.success_response_body import SuccessResponseBody
from ..schemas.session_controller.signin_schema import SigninSchema
from ..services import session_service


@api.post("/signin")
def signin():
    body = SigninSchema().load(request.json)  # type: ignore
    session_service.signin(username=body.get("username"), password=body.get("password"))  # type: ignore
    return SuccessResponseBody(200, "User signed in successfully").to_response()


@api.post("/signout")
@requires_rest_authentication
def signout():
    session_service.signout()
    return SuccessResponseBody(200, "User signed out successfully").to_response(
        remove_session_cookies=True
    )
