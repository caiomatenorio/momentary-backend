from ..common.blueprints.api import api
from ..services import user_service
from ..schemas.sign_up_schema import SignupSchema
from flask import request
from ..dtos.success_response_body import SuccessResponseBody


@api.post("/signup")
def signup():
    body = SignupSchema().load(request.json)
    user_service.create_user(
        name=body.get("name"),
        username=body.get("username"),
        password=body.get("password"),
    )
    return SuccessResponseBody(201, "User created successfully").to_response()
