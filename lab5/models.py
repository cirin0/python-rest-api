from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from pydantic_mongo import ObjectIdField


class Book(BaseModel):
    id: Optional[ObjectIdField] = Field(None, alias="_id")
    title: str
    author: str
    year: int
    genre: str

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "year": 1925,
                "genre": "novel",
            }
        }
