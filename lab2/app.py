import uvicorn
from fastapi import FastAPI
from routes import book_router


app = FastAPI(title="Books API")

app.include_router(book_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)
