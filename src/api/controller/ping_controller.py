from src.api.blueprint.api_bp import api_bp
from src.api.response_body.success_response_body import SuccessResponseBody


@api_bp.get("/ping")
def ping():
    return SuccessResponseBody(200, "Pong!").to_response()
