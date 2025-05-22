from flask import request

from src.api.blueprint.api_bp import api_bp
from src.api.decorator.requires_auth import requires_auth
from src.api.dto.user.get_current_user_response_dto import GetCurrentUserResponseDto
from src.api.response_body.success_response_body import SuccessResponseBody
from src.api.schema.user.update_name_schema import UpdateNameSchema
from src.api.schema.user.update_password_schema import UpdatePasswordSchema
from src.api.schema.user.update_username_schema import UpdateUsernameSchema
from src.service import user_service


@api_bp.get("/users/me")
@requires_auth
def get_current_user():
    user = user_service.get_current_user()
    response_data = GetCurrentUserResponseDto(
        id=user.user_id,
        name=user.name,
        username=user.username,
    )

    return SuccessResponseBody(
        200,
        "User information retrieved successfully.",
        response_data,
    ).to_response()


@api_bp.put("/users/me/name")
@requires_auth
def update_name():
    body = UpdateNameSchema().load(request.json)  # type: ignore
    user_service.update_name(new_name=body["name"])  # type: ignore

    return SuccessResponseBody(200, "User name updated successfully.").to_response()


@api_bp.put("/users/me/username")
@requires_auth
def update_username():
    body = UpdateUsernameSchema().load(request.json)  # type: ignore
    user_service.update_username(new_username=body["username"])  # type: ignore

    return SuccessResponseBody(200, "User username updated successfully.").to_response()


@api_bp.put("/users/me/password")
@requires_auth
def update_password():
    body = UpdatePasswordSchema().load(request.json)  # type: ignore
    user_service.update_password(
        old_password=body["old_password"],  # type: ignore
        new_password=body["new_password"],  # type: ignore
    )

    return SuccessResponseBody(200, "User password updated successfully.").to_response()
