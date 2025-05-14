from ..config import api_bp
from ..dtos.success_response_body import SuccessResponseBody

@api_bp.get("/ping")
def ping():
    return SuccessResponseBody(200, "Pong!").to_response()