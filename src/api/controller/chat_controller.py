from flask import request

from src.api.blueprint.api_bp import api_bp
from src.api.decorator.requires_auth import requires_auth
from src.api.dto.chat.create_chat_response_dto import CreateChatResponseDto
from src.api.dto.chat.get_chat_response_dto import GetChatResponseDto
from src.api.response_body.success_response_body import SuccessResponseBody
from src.api.schema.chat.create_direct_chat_schema import CreateDirectChatSchema
from src.api.schema.chat.get_chat_by_id_schema import GetChatByIdSchema
from src.service import chat_service


@api_bp.get("/chats")
@requires_auth
def get_all_chats():
    chats = chat_service.get_all_chats()
    response_data = list(map(GetChatResponseDto.from_chat, chats))

    return SuccessResponseBody(
        200,
        "Chats retrieved successfully.",
        response_data,
    ).to_response()


@api_bp.get("/chats/<chat_id>")
@requires_auth
def get_chat_by_id(chat_id: str):
    params = GetChatByIdSchema().load({"chat_id": chat_id})
    chat = chat_service.get_chat_by_id_or_raise(params["chat_id"])  # type: ignore
    response_data = GetChatResponseDto.from_chat(chat)

    return SuccessResponseBody(
        200,
        "Chat retrieved successfully.",
        response_data,
    ).to_response()


@api_bp.post("/chats/direct")
@requires_auth
def create_direct_chat():
    body = CreateDirectChatSchema().load(request.json)  # type: ignore
    chat_id = chat_service.create_direct_chat(body["contact_username"])  # type: ignore
    response_data = CreateChatResponseDto(id=chat_id)

    return SuccessResponseBody(201, "Direct chat created.", response_data).to_response()
