import os
from flask import Flask
from routes import book_bp
from models import db, Book, INITIAL_BOOKS
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@db:5432/books_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(book_bp, url_prefix="/api/v1")

    with app.app_context():
        db.create_all()
        if Book.query.count() == 0:
            for book_data in INITIAL_BOOKS:
                book = Book(
                    title=book_data["title"],
                    author=book_data["author"],
                    year=book_data["year"],
                    genre=book_data["genre"],
                )
                db.session.add(book)
            db.session.commit()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")
