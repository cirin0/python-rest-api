def get_swagger_config():
    """
    Повертає конфігурацію для Swagger UI
    """
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/",
    }

    return swagger_config


def get_swagger_template():
    """
    Повертає шаблон документації Swagger
    """
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Books API",
            "description": "API для управління колекцією книг",
            "version": "1.0",
        },
        "definitions": {
            "Book": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "year": {"type": "integer"},
                    "genre": {"type": "string"},
                },
            },
            "BookInput": {
                "type": "object",
                "required": ["title", "author", "year", "genre"],
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 30,
                    },
                    "author": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 30,
                    },
                    "year": {
                        "type": "integer",
                        "minimum": 1000,
                        "maximum": 2025,
                    },
                    "genre": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 10,
                    },
                },
            },
        },
    }

    return swagger_template
