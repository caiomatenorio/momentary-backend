from marshmallow import Schema, fields, validate


class UpdateUsernameSchema(Schema):
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(
                r"^[a-zA-Z0-9_]+$", error="Username must be alphanumeric or underscore"
            ),
        ],
    )
