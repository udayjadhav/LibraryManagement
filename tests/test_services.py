from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import Book, Borrowing, Member
from app.schemas import (
    BookCreate,
    BookUpdate,
    BorrowBookRequest,
    MemberCreate,
    MemberUpdate,
)
from app.services.book_service import BookService
from app.services.borrowing_service import BorrowingService
from app.services.member_service import MemberService


@pytest.mark.asyncio
async def test_book_service_update_not_found():
    repo = AsyncMock()
    repo.get.return_value = None
    service = BookService(repo)

    with pytest.raises(NotFoundError, match="Book not found"):
        await service.update_book(1, BookUpdate(title="New Title"))


@pytest.mark.asyncio
async def test_book_service_create():
    repo = AsyncMock()
    repo.get_by_title_author.return_value = None
    expected = Book(
        id=1, title="T", author="A", is_borrowed=False, created_at=datetime.now(UTC)
    )
    repo.create.return_value = expected
    service = BookService(repo)

    result = await service.create_book(BookCreate(title="T", author="A"))
    assert result == expected
    repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_book_service_duplicate_on_create_case_insensitive():
    repo = AsyncMock()
    repo.get_by_title_author.return_value = Book(
        id=1, title="Dune", author="Frank Herbert", created_at=datetime.now(UTC)
    )
    service = BookService(repo)

    with pytest.raises(
        ConflictError, match="Book with same title and author already exists"
    ):
        await service.create_book(BookCreate(title=" dune ", author=" FRANK HERBERT "))


@pytest.mark.asyncio
async def test_book_service_duplicate_on_update():
    repo = AsyncMock()
    existing = Book(
        id=2, title="Dune", author="Frank Herbert", created_at=datetime.now(UTC)
    )
    repo.get.return_value = existing
    repo.get_other_by_title_author.return_value = Book(
        id=1, title="Dune", author="Frank Herbert", created_at=datetime.now(UTC)
    )
    service = BookService(repo)

    with pytest.raises(
        ConflictError, match="Book with same title and author already exists"
    ):
        await service.update_book(
            2, BookUpdate(title=" dune ", author=" FRANK HERBERT ")
        )


@pytest.mark.asyncio
async def test_member_service_duplicate_email_on_create():
    repo = AsyncMock()
    repo.get_by_email.return_value = Member(
        id=1, name="X", email="a@example.com", active=True, created_at=datetime.now(UTC)
    )
    service = MemberService(repo)

    with pytest.raises(ConflictError, match="Member email already exists"):
        await service.create_member(MemberCreate(name="Y", email="a@example.com"))


@pytest.mark.asyncio
async def test_member_service_update_not_found():
    repo = AsyncMock()
    repo.get.return_value = None
    service = MemberService(repo)

    with pytest.raises(NotFoundError, match="Member not found"):
        await service.update_member(1, MemberUpdate(name="New"))


@pytest.mark.asyncio
async def test_member_service_duplicate_email_on_update_case_insensitive():
    repo = AsyncMock()
    repo.get.return_value = Member(
        id=2, name="B", email="b@example.com", active=True, created_at=datetime.now(UTC)
    )
    repo.get_by_email.return_value = Member(
        id=1, name="A", email="a@example.com", active=True, created_at=datetime.now(UTC)
    )
    service = MemberService(repo)

    with pytest.raises(ConflictError, match="Member email already exists"):
        await service.update_member(2, MemberUpdate(email="  A@Example.com "))


@pytest.mark.asyncio
async def test_borrowing_service_inactive_member():
    member = Member(
        id=1,
        name="A",
        email="a@example.com",
        active=False,
        created_at=datetime.now(UTC),
    )
    member_repo = AsyncMock()
    member_repo.get.return_value = member
    book_repo = AsyncMock()
    borrowing_repo = AsyncMock()
    service = BorrowingService(borrowing_repo, book_repo, member_repo)

    with pytest.raises(BadRequestError, match="Inactive member cannot borrow books"):
        await service.borrow_book(BorrowBookRequest(member_id=1, book_id=1))


@pytest.mark.asyncio
async def test_borrowing_service_book_already_borrowed():
    member = Member(
        id=1, name="A", email="a@example.com", active=True, created_at=datetime.now(UTC)
    )
    book = Book(
        id=1, title="T", author="A", is_borrowed=True, created_at=datetime.now(UTC)
    )
    member_repo = AsyncMock()
    member_repo.get.return_value = member
    book_repo = AsyncMock()
    book_repo.get.return_value = book
    borrowing_repo = AsyncMock()
    borrowing_repo.get_active_for_book.return_value = None
    service = BorrowingService(borrowing_repo, book_repo, member_repo)

    with pytest.raises(ConflictError, match="Book is already borrowed"):
        await service.borrow_book(BorrowBookRequest(member_id=1, book_id=1))


@pytest.mark.asyncio
async def test_borrowing_service_active_borrowing_conflict_even_if_flag_not_set():
    member = Member(
        id=1, name="A", email="a@example.com", active=True, created_at=datetime.now(UTC)
    )
    book = Book(
        id=1, title="T", author="A", is_borrowed=False, created_at=datetime.now(UTC)
    )
    member_repo = AsyncMock()
    member_repo.get.return_value = member
    book_repo = AsyncMock()
    book_repo.get.return_value = book
    borrowing_repo = AsyncMock()
    borrowing_repo.get_active_for_book.return_value = Borrowing(
        id=99, member_id=1, book_id=1, borrowed_at=datetime.now(UTC)
    )
    service = BorrowingService(borrowing_repo, book_repo, member_repo)

    with pytest.raises(ConflictError, match="Book is already borrowed"):
        await service.borrow_book(BorrowBookRequest(member_id=1, book_id=1))


@pytest.mark.asyncio
async def test_borrowing_service_integrity_error_on_commit():
    member = Member(
        id=1, name="A", email="a@example.com", active=True, created_at=datetime.now(UTC)
    )
    book = Book(
        id=1, title="T", author="A", is_borrowed=False, created_at=datetime.now(UTC)
    )
    member_repo = AsyncMock()
    member_repo.get.return_value = member
    book_repo = AsyncMock()
    book_repo.get.return_value = book
    borrowing_repo = AsyncMock()
    borrowing_repo.get_active_for_book.return_value = None
    borrowing_repo.commit.side_effect = IntegrityError("stmt", {}, Exception())
    service = BorrowingService(borrowing_repo, book_repo, member_repo)

    with pytest.raises(ConflictError, match="Book is already borrowed"):
        await service.borrow_book(BorrowBookRequest(member_id=1, book_id=1))
    borrowing_repo.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_borrowing_service_return_already_returned():
    borrowing = Borrowing(
        id=1,
        member_id=1,
        book_id=1,
        borrowed_at=datetime.now(UTC),
        returned_at=datetime.now(UTC),
    )
    borrowing_repo = AsyncMock()
    borrowing_repo.get.return_value = borrowing
    service = BorrowingService(borrowing_repo, MagicMock(), MagicMock())

    with pytest.raises(ConflictError, match="Book already returned"):
        await service.return_book(1)
