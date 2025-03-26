from fastapi import APIRouter, HTTPException, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from models import Book
from schemas import BookSchema

book_router = APIRouter(tags=["books"])


async def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb


@book_router.get("/", response_model=dict)
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
async def get_books(db: AsyncIOMotorDatabase = Depends(get_db)):
    books = []
    async for book in db.books.find():
        books.append(Book(**book))
    return books


@book_router.get("/books/{book_id}")
async def get_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    book = await db.books.find_one({"_id": ObjectId(book_id)})
    if not book:
        raise HTTPException(status_code=404, detail="Немає книги з таким id")
    return Book(**book)


@book_router.post("/books", status_code=201, response_model=Book)
async def add_book(book_data: BookSchema, db: AsyncIOMotorDatabase = Depends(get_db)):
    book_dict = book_data.model_dump()
    result = await db.books.insert_one(book_dict)

    created_book = await db.books.find_one({"_id": result.inserted_id})

    return Book(**created_book)


@book_router.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await db.books.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Немає книги з таким id")
    return None
