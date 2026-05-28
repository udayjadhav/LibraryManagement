from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.book_repository import BookRepository
from app.repositories.borrowing_repository import BorrowingRepository
from app.repositories.member_repository import MemberRepository
from app.services.book_service import BookService
from app.services.borrowing_service import BorrowingService
from app.services.member_service import MemberService


def get_book_repository(db: Session = Depends(get_db)) -> BookRepository:
    return BookRepository(db)


def get_member_repository(db: Session = Depends(get_db)) -> MemberRepository:
    return MemberRepository(db)


def get_borrowing_repository(db: Session = Depends(get_db)) -> BorrowingRepository:
    return BorrowingRepository(db)


def get_book_service(
    repository: BookRepository = Depends(get_book_repository),
) -> BookService:
    return BookService(repository)


def get_member_service(
    repository: MemberRepository = Depends(get_member_repository),
) -> MemberService:
    return MemberService(repository)


def get_borrowing_service(
    borrowing_repository: BorrowingRepository = Depends(get_borrowing_repository),
    book_repository: BookRepository = Depends(get_book_repository),
    member_repository: MemberRepository = Depends(get_member_repository),
) -> BorrowingService:
    return BorrowingService(borrowing_repository, book_repository, member_repository)
