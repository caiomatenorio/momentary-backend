from ..common.blueprints.api import api
from ..dtos.success_response_body import SuccessResponseBody


@api.get("/ping")
def ping():
    return SuccessResponseBody(200, "Pong!").to_response()
