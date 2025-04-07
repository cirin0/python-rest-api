from flask_restful import Resource, reqparse
from flask import request
from models import Book, db
from schemas import book_schema, books_schema


class BookList(Resource):
    def get(self):
        """
        Отримати список книг з пагінацією
        ---
        parameters:
          - name: cursor
            in: query
            type: integer
            required: false
            description: ID останньої книги з попередньої сторінки
          - name: limit
            in: query
            type: integer
            required: false
            default: 10
            description: Кількість книг на сторінці
        responses:
          200:
            description: Список книг
            schema:
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/definitions/Book'
                meta:
                  type: object
                  properties:
                    total:
                      type: integer
                    limit:
                      type: integer
                    next_cursor:
                      type: integer
                    has_next:
                      type: boolean
        """
        cursor = request.args.get("cursor", default=None, type=int)
        limit = request.args.get("limit", default=10, type=int)

        query = Book.query.order_by(Book.id)
        total_books = Book.query.count()

        if cursor:
            query = query.filter(Book.id > cursor)

        books = query.limit(limit + 1).all()
        has_next = len(books) > limit
        books = books[:limit]

        next_cursor = None
        if has_next and books:
            next_cursor = books[-1].id

        result = {
            "data": books_schema.dump(books),
            "meta": {
                "total": total_books,
                "limit": limit,
                "next_cursor": next_cursor,
                "has_next": has_next,
            },
        }
        return result

    def post(self):
        """
        Додати нову книгу
        ---
        parameters:
          - in: body
            name: book
            description: Дані нової книги
            required: true
            schema:
              $ref: '#/definitions/BookInput'
        responses:
          201:
            description: Книгу успішно додано
            schema:
              $ref: '#/definitions/Book'
          400:
            description: Помилка валідації
            schema:
              properties:
                errors:
                  type: object
        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            "title", type=str, required=True, help="Заголовок не може бути пустим"
        )
        parser.add_argument(
            "author", type=str, required=True, help="Автор не може бути пустим"
        )
        parser.add_argument(
            "year", type=int, required=True, help="Рік не може бути пустим"
        )
        parser.add_argument(
            "genre", type=str, required=True, help="Жанр не може бути пустим"
        )

        args = parser.parse_args()

        # Валідація через marshmallow
        errors = book_schema.validate(args)
        if errors:
            return {"errors": errors}, 400

        new_book = Book(
            title=args["title"],
            author=args["author"],
            year=args["year"],
            genre=args["genre"],
        )

        db.session.add(new_book)
        db.session.commit()

        return book_schema.dump(new_book), 201


class BookDetail(Resource):
    def get(self, book_id):
        """
        Отримати інформацію про книгу за ID
        ---
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
            description: ID книги
        responses:
          200:
            description: Деталі книги
            schema:
              $ref: '#/definitions/Book'
          404:
            description: Книгу не знайдено
            schema:
              properties:
                error:
                  type: string
        """
        book = Book.query.get(book_id)
        if book:
            return book_schema.dump(book)
        return {"error": "Немає книги з таким id"}, 404

    def put(self, book_id):
        """
        Оновити книгу за ID
        ---
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
            description: ID книги
          - in: body
            name: book
            description: Оновлені дані книги
            required: true
            schema:
              $ref: '#/definitions/BookInput'
        responses:
          200:
            description: Книгу успішно оновлено
            schema:
              $ref: '#/definitions/Book'
          400:
            description: Помилка валідації
            schema:
              properties:
                errors:
                  type: object
          404:
            description: Книгу не знайдено
            schema:
              properties:
                error:
                  type: string
        """
        book = Book.query.get(book_id)
        if not book:
            return {"error": "Немає книги з таким id"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument(
            "title", type=str, required=True, help="Заголовок не може бути пустим"
        )
        parser.add_argument(
            "author", type=str, required=True, help="Автор не може бути пустим"
        )
        parser.add_argument(
            "year", type=int, required=True, help="Рік не може бути пустим"
        )
        parser.add_argument(
            "genre", type=str, required=True, help="Жанр не може бути пустим"
        )

        args = parser.parse_args()

        # Валідація через marshmallow
        errors = book_schema.validate(args)
        if errors:
            return {"errors": errors}, 400

        # Оновлення даних книги
        book.title = args["title"]
        book.author = args["author"]
        book.year = args["year"]
        book.genre = args["genre"]

        db.session.commit()

        return book_schema.dump(book), 200

    def delete(self, book_id):
        """
        Видалити книгу за ID
        ---
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
            description: ID книги
        responses:
          204:
            description: Книгу успішно видалено
          404:
            description: Книгу не знайдено
            schema:
              properties:
                error:
                  type: string
        """
        book = Book.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return "", 204
        return {"error": "Немає книги з таким id"}, 404
