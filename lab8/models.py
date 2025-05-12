from sqlalchemy import Column, Integer, String
from database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    year = Column(Integer)
    genre = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)
