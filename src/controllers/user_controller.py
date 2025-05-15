from flask import request

from ..blueprints.api import api
from ..decorators.requires_authentication import requires_authentication
from ..dtos.success_response_body import SuccessResponseBody
from ..schemas.user_controller.signup_schema import SignupSchema
from ..schemas.user_controller.update_name_schema import UpdateNameSchema
from ..schemas.user_controller.update_username_schema import UpdateUsernameSchema
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


@api.get("/me/whoami")
@requires_authentication(request)
def whoami():
    user = user_service.whoami()
    return SuccessResponseBody(
        200, "User information retrieved successfully", user
    ).to_response()


@api.put("/me/name")
@requires_authentication(request)
def update_name():
    body = UpdateNameSchema().load(request.json)
    user_service.update_name(body.get("name"))
    return SuccessResponseBody(200, "User name updated successfully").to_response()


@api.put("/me/username")
@requires_authentication(request)
def update_username():
    body = UpdateUsernameSchema().load(request.json)
    user_service.update_username(body.get("username"))
    return SuccessResponseBody(200, "User username updated successfully").to_response()
