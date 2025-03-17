from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any

from models import BOOKS, Book, generate_new_book_id
from schemas import BookSchema

book_router = APIRouter(tags=["books"])


async def get_book_by_id(book_id: int) -> Book:
    return next((b for b in BOOKS if b.id == book_id), None)


@book_router.get("/", response_model=Dict[str, Any])
async def index():
    return {
        "message": "Welcome to the Books API",
        "endpoints": {
            "GET /books": "Get all books",
            "GET /books/<id>": "Get a specific book by ID",
            "POST /books": "Add a new book",
            "DELETE /books/<id>": "Delete a book by ID",
        },
    }


@book_router.get("/books")
async def get_books():
    return [asdict(book) for book in BOOKS]


@book_router.get("/books/{book_id}")
async def get_book(book_id: int):
    book = await get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Немає книги з таким id")
    return asdict(book)


@book_router.post("/books", status_code=201)
async def add_book(book_data: BookSchema):
    id = generate_new_book_id()

    new_book = Book(
        id=id,
        title=book_data.title,
        author=book_data.author,
        year=book_data.year,
        genre=book_data.genre,
    )
    BOOKS.append(new_book)
    return asdict(new_book)


@book_router.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: int):
    book = await get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Немає книги з таким id")
    BOOKS.remove(book)
    return Response(status_code=204)
