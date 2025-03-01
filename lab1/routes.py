from flask import Blueprint, jsonify, request
from schemas import book_schema, books_schema
from models import BOOKS, Book

book_bp = Blueprint("books", __name__)


def get_book_by_id(book_id):
    return next((b for b in BOOKS if b.id == book_id), None)


@book_bp.route("/books", methods=["GET"])
def get_books():
    return jsonify(books_schema.dump(BOOKS))


@book_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = get_book_by_id(book_id)
    if book:
        return jsonify(book_schema.dump(book))
    else:
        return "Немає книги з таким id", 404


@book_bp.route("/books", methods=["POST"])
def add_book():
    data = request.get_json()
    errors = book_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    id = max([b.id for b in BOOKS]) + 1
    new_book = Book(
        id=id,
        title=data["title"],
        author=data["author"],
        year=data["year"],
        genre=data["genre"],
    )
    BOOKS.append(new_book)
    return jsonify(book_schema.dump(new_book)), 201


@book_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = get_book_by_id(book_id)
    if book:
        BOOKS.remove(book)
        return "", 204
    return "Немає книги з таким id", 404
