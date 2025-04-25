from fastapi import APIRouter, HTTPException, Depends, Header
from database import SessionLocal
from auth_service import decode_token
from models import Book
from schemas import BookSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

book_router = APIRouter(tags=["books"])


@book_router.get("/", response_model=dict)
async def index():
    return {
        "message": "Welcome to the Books API",
        "endpoints": {
            "GET /books": "Get all books",
            "GET /books/<id>": "Get a specific book by ID",
            "POST /books": "Add a new book",
            "DELETE /books/<id>": "Delete a book by ID",
            "POST /token": "Get access token",
            "POST /token/refresh": "Refresh access token",
            "POST /register": "Register a new user",
        },
    }


async def get_current_user(authorization: str = Header(...)):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]


@book_router.get("/books", response_model=list[BookSchema], status_code=200)
async def get_books(
    user=Depends(get_current_user), db: AsyncSession = Depends(lambda: SessionLocal())
):
    result = db.execute(select(Book))
    return result.scalars().all()


@book_router.get("/books/{book_id}", response_model=BookSchema, status_code=200)
async def get_book_by_id(
    book_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: SessionLocal()),
):
    result = db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@book_router.post("/books", status_code=201, response_model=BookSchema)
async def add_book(
    book: BookSchema,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: SessionLocal()),
):
    new_book = Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@book_router.delete("/books/{book_id}", status_code=204)
async def delete_book(
    book_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: SessionLocal()),
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return None
