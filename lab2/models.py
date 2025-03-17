from dataclasses import dataclass, field
from typing import List


@dataclass
class Book:
    title: str
    author: str
    year: int
    genre: str
    id: int = field(default=None)


BOOKS: List[Book] = [
    Book(id=1, title="Кобзар", author="Тарас Шевченко", year=1840, genre="Поема"),
    Book(id=2, title="Маруся Чурай", author="Ліна Костенко", year=1973, genre="Поема"),
]


def generate_new_book_id():
    return max([book.id for book in BOOKS]) + 1 if BOOKS else 1
