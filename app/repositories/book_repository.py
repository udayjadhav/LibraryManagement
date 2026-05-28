from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Book


class BookRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, **fields) -> Book:
        book = Book(**fields)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def get(self, book_id: int) -> Book | None:
        return self.db.get(Book, book_id)

    def list_all(self) -> list[Book]:
        return list(self.db.scalars(select(Book).order_by(Book.id)))

    def get_by_title_author(self, title: str, author: str) -> Book | None:
        return self.db.scalar(
            select(Book).where(
                func.lower(func.trim(Book.title)) == title,
                func.lower(func.trim(Book.author)) == author,
            )
        )

    def get_other_by_title_author(
        self, title: str, author: str, exclude_id: int
    ) -> Book | None:
        return self.db.scalar(
            select(Book).where(
                func.lower(func.trim(Book.title)) == title,
                func.lower(func.trim(Book.author)) == author,
                Book.id != exclude_id,
            )
        )

    def save(self, book: Book) -> Book:
        self.db.commit()
        self.db.refresh(book)
        return book
