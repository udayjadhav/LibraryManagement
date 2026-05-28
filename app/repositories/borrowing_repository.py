from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Borrowing


class BorrowingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, borrowing_id: int) -> Borrowing | None:
        return await self.db.get(Borrowing, borrowing_id)

    async def get_active_for_book(self, book_id: int) -> Borrowing | None:
        return await self.db.scalar(
            select(Borrowing).where(
                Borrowing.book_id == book_id, Borrowing.returned_at.is_(None)
            )
        )

    async def get_other_active_for_book(
        self, book_id: int, exclude_id: int
    ) -> Borrowing | None:
        return await self.db.scalar(
            select(Borrowing).where(
                Borrowing.book_id == book_id,
                Borrowing.returned_at.is_(None),
                Borrowing.id != exclude_id,
            )
        )

    async def list_borrowings(
        self, member_id: int | None = None, active_only: bool = True
    ) -> list[Borrowing]:
        statement: Select[tuple[Borrowing]] = select(Borrowing).order_by(Borrowing.id)
        if member_id is not None:
            statement = statement.where(Borrowing.member_id == member_id)
        if active_only:
            statement = statement.where(Borrowing.returned_at.is_(None))
        result = await self.db.scalars(statement)
        return list(result)

    async def add(self, borrowing: Borrowing) -> None:
        self.db.add(borrowing)

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def refresh(self, borrowing: Borrowing) -> Borrowing:
        await self.db.refresh(borrowing)
        return borrowing
