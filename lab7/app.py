import uvicorn
from fastapi import FastAPI
from database import engine
from routes import book_router
from auth import auth_router
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Books API")

app.include_router(book_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
