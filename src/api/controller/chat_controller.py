from flask import request

from src.api.blueprint.api_bp import api_bp
from src.api.decorator.requires_auth import requires_auth
from src.api.response_body.success_response_body import SuccessResponseBody
from src.api.schema.chat.create_direct_chat_schema import CreateDirectChatSchema
from src.service import chat_service


@api_bp.post("chats/direct")
@requires_auth
def create_direct_chat():
    body = CreateDirectChatSchema().load(request.json)  # type: ignore
    chat_id = chat_service.create_direct_chat(body["contact_username"])  # type: ignore
    return SuccessResponseBody(
        201,
        "Direct chat created.",
        {"chat_id": chat_id},
    ).to_response()
