from marshmallow import Schema, fields


class GetChatByIdSchema(Schema):
    chat_id = fields.UUID(required=True)
