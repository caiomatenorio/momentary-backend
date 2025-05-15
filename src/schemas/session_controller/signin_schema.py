from marshmallow import Schema, fields


class SigninSchema(Schema):
    username = fields.Str(required=True)

    password = fields.Str(required=True)
