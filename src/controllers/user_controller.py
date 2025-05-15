from flask import request

from ..common.blueprints.api import api
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
