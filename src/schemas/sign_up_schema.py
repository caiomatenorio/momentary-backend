from marshmallow import Schema, fields, validate

class SignupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    username = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    password = fields.Str(required=True)