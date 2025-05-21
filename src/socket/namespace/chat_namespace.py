from flask_socketio import Namespace, emit

from src.service import chat_service
from src.socket.decorator.handle_auth_namespace_connection import (
    handle_auth_namespace_connection,
)
from src.socket.decorator.handle_auth_namespace_disconnection import (
    handle_auth_namespace_disconnection,
)
from src.socket.dto.chat.new_message_dto import NewMessageDto
from src.socket.error_handler import error_handler
from src.socket.response_body import ResponseBody
from src.socket.schema.chat.send_message_schema import SendMessageSchema


class ChatNamespace(Namespace):
    @handle_auth_namespace_connection
    def on_connect(self):
        chat_service.connect_to_all_chats()

    def on_send_message(self, data):
        try:
            data = SendMessageSchema().load(data)
            message = chat_service.send_message(data["chat_id"], data["content"])  # type: ignore
            response_data = NewMessageDto.from_message(message)

            emit(
                "new_message",
                ResponseBody(
                    message="New message coming.",
                    data=response_data.__dict__,
                ).to_dict(),
                to=str(message.chat_id),
            )
        except Exception as e:
            error_handler(e)

    @handle_auth_namespace_disconnection
    def on_disconnect(self): ...
