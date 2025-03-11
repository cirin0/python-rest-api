from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
        }


# Початкові дані для заповнення бази даних
INITIAL_BOOKS = [
    {
        "id": 1,
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "year": 1840,
        "genre": "Поема",
    },
    {
        "id": 2,
        "title": "Маруся Чурай",
        "author": "Ліна Костенко",
        "year": 1973,
        "genre": "Поема",
    },
]
