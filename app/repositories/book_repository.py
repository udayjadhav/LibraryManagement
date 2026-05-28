from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book


class BookRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **fields) -> Book:
        book = Book(**fields)
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def get(self, book_id: int) -> Book | None:
        return await self.db.get(Book, book_id)

    async def list_all(self) -> list[Book]:
        result = await self.db.scalars(select(Book).order_by(Book.id))
        return list(result)

    async def get_by_title_author(self, title: str, author: str) -> Book | None:
        return await self.db.scalar(
            select(Book).where(
                func.lower(func.trim(Book.title)) == title,
                func.lower(func.trim(Book.author)) == author,
            )
        )

    async def get_other_by_title_author(
        self, title: str, author: str, exclude_id: int
    ) -> Book | None:
        return await self.db.scalar(
            select(Book).where(
                func.lower(func.trim(Book.title)) == title,
                func.lower(func.trim(Book.author)) == author,
                Book.id != exclude_id,
            )
        )

    async def save(self, book: Book) -> Book:
        await self.db.commit()
        await self.db.refresh(book)
        return book
