from marshmallow import Schema, fields


class SendMessageSchema(Schema):
    chat_id = fields.UUID(required=True)

    content = fields.Str(required=True)
