from marshmallow import Schema, fields, validate


class UpdatePasswordSchema(Schema):
    old_password = fields.Str(required=True)

    new_password = fields.Str(
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
