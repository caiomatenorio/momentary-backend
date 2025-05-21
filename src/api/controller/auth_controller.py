from flask import request

from src.api.blueprint.api_bp import api_bp
from src.api.decorator.requires_auth import requires_auth
from src.api.response_body.success_response_body import SuccessResponseBody
from src.api.schema.auth.signin_schema import SigninSchema
from src.api.schema.auth.signup_schema import SignupSchema
from src.service import auth_service


@api_bp.post("auth/signup")
def signup():
    body = SignupSchema().load(request.json)  # type: ignore
    auth_service.signup(
        name=body["name"],  # type: ignore
        username=body["username"],  # type: ignore
        password=body["password"],  # type: ignore
    )
    return SuccessResponseBody(201, "User created successfully.").to_response()


@api_bp.post("auth/signin")
def signin():
    body = SigninSchema().load(request.json)  # type: ignore
    auth_service.signin(username=body["username"], password=body["password"])  # type: ignore
    return SuccessResponseBody(200, "User signed in successfully.").to_response()


@api_bp.post("auth/signout")
@requires_auth
def signout():
    auth_service.signout()
    return SuccessResponseBody(200, "User signed out successfully.").to_response(
        clear_session=True
    )
