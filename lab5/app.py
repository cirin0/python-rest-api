import contextlib
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import book_router
from typing import AsyncIterator


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.mongodb_client = AsyncIOMotorClient(
        "mongodb://mongo_admin:password@mongo:27017"
    )
    app.mongodb = app.mongodb_client.books_db
    yield
    app.mongodb_client.close()


app = FastAPI(title="Books API", lifespan=lifespan)

app.include_router(book_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
