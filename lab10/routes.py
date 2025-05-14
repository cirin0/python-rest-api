from fastapi import APIRouter, HTTPException, Depends, Header, Request
from database import get_db
from auth_service import decode_token
from models import Book
from schemas import BookSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from rate_limiter import RateLimiter

book_router = APIRouter(tags=["books"])

limiter = RateLimiter()


@book_router.get("/", response_model=dict)
async def index(request: Request):
    return {
        "message": "Welcome to the Books API",
        "endpoints": {
            "GET /books": "Get all books",
            "GET /books/<id>": "Get a specific book by ID",
            "POST /books": "Add a new book",
            "DELETE /books/<id>": "Delete a book by ID",
            "POST /login": "Get access token",
            "POST /token/refresh": "Refresh access token",
            "POST /register": "Register a new user",
        },
    }


async def get_user_if_authenticated(authorization: str = Header(None)):
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return None
    payload = decode_token(token)
    if not payload:
        return None
    return payload["sub"]


@book_router.get("/books", response_model=list[BookSchema], status_code=200)
async def get_books(
    request: Request,
    user: str = Depends(get_user_if_authenticated),
    db: AsyncSession = Depends(get_db),
):
    # await limiter.check_rate_limit(request, user if user else None)
    result = await db.execute(select(Book))
    return result.scalars().all()


@book_router.get("/books/{book_id}", response_model=BookSchema, status_code=200)
async def get_book_by_id(
    request: Request,
    book_id: int,
    user: str = Depends(get_user_if_authenticated),
    db: AsyncSession = Depends(get_db),
):
    await limiter.check_rate_limit(request, user if user else None)
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@book_router.post("/books", status_code=201, response_model=BookSchema)
async def add_book(
    request: Request,
    book: BookSchema,
    user: str = Depends(get_user_if_authenticated),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    await limiter.check_rate_limit(request, user)
    new_book = Book(**book.model_dump())
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book


@book_router.delete("/books/{book_id}", status_code=204)
async def delete_book(
    request: Request,
    book_id: int,
    user: str = Depends(get_user_if_authenticated),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    await limiter.check_rate_limit(request, user)
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    await db.delete(book)
    await db.commit()
    return None
