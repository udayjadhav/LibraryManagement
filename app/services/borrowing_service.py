from datetime import datetime, UTC

from sqlalchemy.exc import IntegrityError

from app.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import Borrowing
from app.repositories.book_repository import BookRepository
from app.repositories.borrowing_repository import BorrowingRepository
from app.repositories.member_repository import MemberRepository
from app.schemas import BorrowBookRequest


class BorrowingService:
    def __init__(
        self,
        borrowing_repository: BorrowingRepository,
        book_repository: BookRepository,
        member_repository: MemberRepository,
    ) -> None:
        self.borrowing_repository = borrowing_repository
        self.book_repository = book_repository
        self.member_repository = member_repository

    async def borrow_book(self, payload: BorrowBookRequest) -> Borrowing:
        member = await self.member_repository.get(payload.member_id)
        if not member:
            raise NotFoundError("Member not found")
        if not member.active:
            raise BadRequestError("Inactive member cannot borrow books")

        book = await self.book_repository.get(payload.book_id)
        if not book:
            raise NotFoundError("Book not found")

        active_borrowing = await self.borrowing_repository.get_active_for_book(book.id)
        if book.is_borrowed or active_borrowing:
            raise ConflictError("Book is already borrowed")

        borrowing = Borrowing(member_id=member.id, book_id=book.id)
        book.is_borrowed = True
        await self.borrowing_repository.add(borrowing)
        try:
            await self.borrowing_repository.commit()
        except IntegrityError:
            await self.borrowing_repository.rollback()
            raise ConflictError("Book is already borrowed")
        return await self.borrowing_repository.refresh(borrowing)

    async def return_book(self, borrowing_id: int) -> Borrowing:
        borrowing = await self.borrowing_repository.get(borrowing_id)
        if not borrowing:
            raise NotFoundError("Borrowing record not found")
        if borrowing.returned_at is not None:
            raise ConflictError("Book already returned")

        borrowing.returned_at = datetime.now(UTC)
        still_active = await self.borrowing_repository.get_other_active_for_book(
            borrowing.book_id, borrowing.id
        )
        book = await self.book_repository.get(borrowing.book_id)
        if book:
            book.is_borrowed = still_active is not None
        await self.borrowing_repository.commit()
        return await self.borrowing_repository.refresh(borrowing)

    async def list_borrowings(
        self, member_id: int | None = None, active_only: bool = True
    ) -> list[Borrowing]:
        return await self.borrowing_repository.list_borrowings(member_id, active_only)
