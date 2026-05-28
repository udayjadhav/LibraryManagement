from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models import Borrowing


class BorrowingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, borrowing_id: int) -> Borrowing | None:
        return self.db.get(Borrowing, borrowing_id)

    def get_active_for_book(self, book_id: int) -> Borrowing | None:
        return self.db.scalar(
            select(Borrowing).where(
                Borrowing.book_id == book_id, Borrowing.returned_at.is_(None)
            )
        )

    def get_other_active_for_book(
        self, book_id: int, exclude_id: int
    ) -> Borrowing | None:
        return self.db.scalar(
            select(Borrowing).where(
                Borrowing.book_id == book_id,
                Borrowing.returned_at.is_(None),
                Borrowing.id != exclude_id,
            )
        )

    def list_borrowings(
        self, member_id: int | None = None, active_only: bool = True
    ) -> list[Borrowing]:
        statement: Select[tuple[Borrowing]] = select(Borrowing).order_by(Borrowing.id)
        if member_id is not None:
            statement = statement.where(Borrowing.member_id == member_id)
        if active_only:
            statement = statement.where(Borrowing.returned_at.is_(None))
        return list(self.db.scalars(statement))

    def add(self, borrowing: Borrowing) -> None:
        self.db.add(borrowing)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, borrowing: Borrowing) -> Borrowing:
        self.db.refresh(borrowing)
        return borrowing
