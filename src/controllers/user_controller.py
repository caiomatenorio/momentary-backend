from flask import request

from ..blueprints.api import api
from ..decorators.requires_authentication import requires_authentication
from ..dtos.success_response_body import SuccessResponseBody
from ..schemas.signup_schema import SignupSchema
from ..services import user_service


@api.post("/signup")
def signup():
    body = SignupSchema().load(request.json)
    user_service.create_user(
        name=body.get("name"),
        username=body.get("username"),
        password=body.get("password"),
    )
    return SuccessResponseBody(201, "User created successfully").to_response()


@api.get("/whoami")
@requires_authentication(request)
def whoami():
    user = user_service.whoami()
    return SuccessResponseBody(
        200, "User information retrieved successfully", user
    ).to_response()
