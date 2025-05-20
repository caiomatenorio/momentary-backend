from marshmallow import Schema, fields, validate


class SignupSchema(Schema):
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(
                r"^(?=.*\S).+$",
                error="Name must contain at least one non-blank character",
            ),
        ],
    )

    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(
                r"^[a-zA-Z0-9_]+$", error="Username must be alphanumeric or underscore"
            ),
        ],
    )

    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(
                r"^(?=.*[A-Z]).*$",
                error="Password must contain at least one uppercase letter",
            ),
            validate.Regexp(
                r"^(?=.*[a-z]).*$",
                error="Password must contain at least one lowercase letter",
            ),
            validate.Regexp(
                r"^(?=.*\d).*$", error="Password must contain at least one digit"
            ),
            validate.Regexp(
                r"^(?=.*[@$!%*?&]).*$",
                error="Password must contain at least one special character",
            ),
        ],
    )
