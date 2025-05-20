from marshmallow import Schema, fields, validate


class UpdateNameSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
