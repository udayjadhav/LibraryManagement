from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_borrowing_service
from app.models import Borrowing
from app.schemas import BorrowBookRequest, BorrowingOut
from app.services.borrowing_service import BorrowingService

router = APIRouter(prefix="/borrowings", tags=["borrowings"])

VALIDATION_ERROR = {
    422: {"description": "Request validation failed (invalid body or query params)"}
}


@router.post(
    "/borrow",
    response_model=BorrowingOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Inactive member cannot borrow books"},
        404: {"description": "Member or book not found"},
        409: {"description": "Book is already borrowed"},
        **VALIDATION_ERROR,
    },
)
def borrow_book(
    payload: BorrowBookRequest,
    service: BorrowingService = Depends(get_borrowing_service),
) -> Borrowing:
    return service.borrow_book(payload)


@router.post(
    "/{borrowing_id}/return",
    response_model=BorrowingOut,
    responses={
        404: {"description": "Borrowing record not found"},
        409: {"description": "Book already returned"},
    },
)
def return_book(
    borrowing_id: int, service: BorrowingService = Depends(get_borrowing_service)
) -> Borrowing:
    return service.return_book(borrowing_id)


@router.get("", response_model=list[BorrowingOut])
def list_borrowings(
    member_id: int | None = Query(default=None),
    active_only: bool = Query(default=True),
    service: BorrowingService = Depends(get_borrowing_service),
) -> list[Borrowing]:
    return service.list_borrowings(member_id, active_only)
