from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError, NotFoundError
from app.models import Book
from app.repositories.book_repository import BookRepository
from app.schemas import BookCreate, BookUpdate


class BookService:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def create_book(self, payload: BookCreate) -> Book:
        title = payload.title.strip()
        author = payload.author.strip()
        normalized_title, normalized_author = self._normalized_book_key(title, author)
        if self.repository.get_by_title_author(normalized_title, normalized_author):
            raise ConflictError("Book with same title and author already exists")

        try:
            return self.repository.create(
                title=title, author=author, description=payload.description
            )
        except IntegrityError as exc:
            raise ConflictError(
                "Book with same title and author already exists"
            ) from exc

    def update_book(self, book_id: int, payload: BookUpdate) -> Book:
        book = self.repository.get(book_id)
        if not book:
            raise NotFoundError("Book not found")

        updated_fields = payload.model_dump(exclude_unset=True)
        if "title" in updated_fields:
            updated_fields["title"] = updated_fields["title"].strip()
        if "author" in updated_fields:
            updated_fields["author"] = updated_fields["author"].strip()

        next_title = updated_fields.get("title", book.title)
        next_author = updated_fields.get("author", book.author)
        normalized_title, normalized_author = self._normalized_book_key(
            next_title, next_author
        )
        if self.repository.get_other_by_title_author(
            normalized_title, normalized_author, book_id
        ):
            raise ConflictError("Book with same title and author already exists")

        for key, value in updated_fields.items():
            setattr(book, key, value)

        try:
            return self.repository.save(book)
        except IntegrityError as exc:
            raise ConflictError(
                "Book with same title and author already exists"
            ) from exc

    def list_books(self) -> list[Book]:
        return self.repository.list_all()

    @staticmethod
    def _normalized_book_key(title: str, author: str) -> tuple[str, str]:
        return title.strip().lower(), author.strip().lower()
