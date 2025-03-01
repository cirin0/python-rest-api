from flask import Flask
from routes import book_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(book_bp, url_prefix="/v1/api")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
