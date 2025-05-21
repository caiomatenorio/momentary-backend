from marshmallow import Schema, fields


class CreateDirectChatSchema(Schema):
    contact_username = fields.String(required=True)
