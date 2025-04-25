from pydantic import BaseModel, Field, field_validator


class BookSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=30)
    author: str = Field(..., min_length=3, max_length=30)
    year: int = Field(..., gt=999, lt=2026)
    genre: str = Field(..., min_length=2, max_length=10)

    @field_validator("year")
    def validate_year(cls, year):
        if year < 1000 or year > 2025:
            raise ValueError("Year must be between 1000 and 2025")
        return year


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)


class Token(BaseModel):
    access_token: str
    refresh_token: str
