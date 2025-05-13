import uvicorn
from fastapi import FastAPI
from routes import book_router
from auth import auth_router
from rate_limiter import RateLimiter
import models
import os
from database import async_engine

app = FastAPI(title="Books API")


@app.on_event("startup")
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        print("Database tables created successfully!")


limiter = RateLimiter()

app.include_router(book_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
