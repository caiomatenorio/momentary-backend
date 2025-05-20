from flask import request

from ..blueprints.api import api
from ..decorators.requires_rest_auth import requires_rest_auth
from ..dtos.success_response_body import SuccessResponseBody
from ..schemas.user_controller.signup_schema import SignupSchema
from ..schemas.user_controller.update_name_schema import UpdateNameSchema
from ..schemas.user_controller.update_password_schema import UpdatePasswordSchema
from ..schemas.user_controller.update_username_schema import UpdateUsernameSchema
from ..services import user_service


@api.post("/signup")
def signup():
    body = SignupSchema().load(request.json)  # type: ignore
    user_service.create_user(
        name=body.get("name"),  # type: ignore
        username=body.get("username"),  # type: ignore
        password=body.get("password"),  # type: ignore
    )
    return SuccessResponseBody(201, "User created successfully").to_response()


@api.get("users/me")
@requires_rest_auth
def whoami():
    user = user_service.whoami()
    return SuccessResponseBody(
        200, "User information retrieved successfully", user
    ).to_response()


@api.put("users/me/name")
@requires_rest_auth
def update_name():
    body = UpdateNameSchema().load(request.json)  # type: ignore
    user_service.update_name(name=body.get("name"))  # type: ignore
    return SuccessResponseBody(200, "User name updated successfully").to_response()


@api.put("users/me/username")
@requires_rest_auth
def update_username():
    body = UpdateUsernameSchema().load(request.json)  # type: ignore
    user_service.update_username(username=body.get("username"))  # type: ignore
    return SuccessResponseBody(200, "User username updated successfully").to_response()


@api.put("users/me/password")
@requires_rest_auth
def update_password():
    body = UpdatePasswordSchema().load(request.json)  # type: ignore
    user_service.update_password(
        old_password=body.get("old_password"),  # type: ignore
        new_password=body.get("new_password"),  # type: ignore
    )
    return SuccessResponseBody(200, "User password updated successfully").to_response()
