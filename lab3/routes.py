from flask import Blueprint, jsonify, request
from schemas import book_schema, books_schema
from models import db, Book

book_bp = Blueprint("books", __name__)


def get_book_by_id(book_id: int) -> Book:
    return Book.query.get(book_id)


@book_bp.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "message": "Welcome to the Books API",
            "endpoints": {
                "GET /books": "Get all books (supports pagination with limit and offset parameters)",
                "GET /books/<id>": "Get a specific book by ID",
                "POST /books": "Add a new book",
                "DELETE /books/<id>": "Delete a book by ID",
            },
        }
    )


@book_bp.route("/books", methods=["GET"])
def get_books():
    limit = request.args.get("limit", default=None, type=int)
    offset = request.args.get("offset", default=0, type=int)

    query = Book.query
    if limit:
        query = query.limit(limit).offset(offset)
    books = query.all()
    total_books = Book.query.count()

    result = {
        "data": books_schema.dump(books),
        "meta": {
            "total": total_books,
            "limit": limit,
            "offset": offset,
            "has_more": limit and (offset + limit) < total_books,
        },
    }
    return jsonify(result)


@book_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = get_book_by_id(book_id)
    if book:
        return jsonify(book_schema.dump(book))
    else:
        return jsonify({"error": "Немає книги з таким id"}), 404


@book_bp.route("/books", methods=["POST"])
def add_book():
    data = request.get_json()
    errors = book_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    new_book = Book(
        title=data["title"],
        author=data["author"],
        year=data["year"],
        genre=data["genre"],
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify(book_schema.dump(new_book)), 201


@book_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = get_book_by_id(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Книгу успішно видалено"}), 204
    return jsonify({"error": "Немає книги з таким id"}), 404
