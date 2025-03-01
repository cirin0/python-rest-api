from marshmallow import Schema, fields, validate


class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=30))
    author = fields.Str(required=True, validate=validate.Length(min=3, max=30))
    year = fields.Int(
        required=True,
        validate=[
            validate.Range(min=1000, max=2025, error="Рік повинен бути між 1000 і 2025")
        ],
    )
    genre = fields.Str(required=True, validate=validate.Length(min=2, max=10))


book_schema = BookSchema()
books_schema = BookSchema(many=True)
