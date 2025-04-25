from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import User
from database import get_db
from schemas import Token, UserCreate
from auth_service import (
    decode_token,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_password,
)

auth_router = APIRouter(tags=["auth"])


@auth_router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = db.execute(select(User).where(User.username == user.username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created"}


@auth_router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"sub": user.username})
    refresh = create_refresh_token({"sub": user.username})
    return {"access_token": access, "refresh_token": refresh}


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(token_data: dict):
    if "token" not in token_data:
        raise HTTPException(status_code=400, detail="Token is required")

    payload = decode_token(token_data["token"])
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    access = create_access_token({"sub": payload["sub"]})
    refresh = create_refresh_token({"sub": payload["sub"]})
    return {"access_token": access, "refresh_token": refresh}
