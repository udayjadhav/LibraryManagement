from fastapi import APIRouter, Depends, status

from app.dependencies import get_book_service
from app.models import Book
from app.schemas import BookCreate, BookOut, BookUpdate
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])

VALIDATION_ERROR = {
    422: {"description": "Request validation failed (invalid body or query params)"}
}


@router.post(
    "",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Book with same title and author already exists"},
        **VALIDATION_ERROR,
    },
)
def create_book(
    payload: BookCreate, service: BookService = Depends(get_book_service)
) -> Book:
    return service.create_book(payload)


@router.put(
    "/{book_id}",
    response_model=BookOut,
    responses={
        404: {"description": "Book not found"},
        409: {"description": "Book with same title and author already exists"},
        **VALIDATION_ERROR,
    },
)
def update_book(
    book_id: int, payload: BookUpdate, service: BookService = Depends(get_book_service)
) -> Book:
    return service.update_book(book_id, payload)


@router.get("", response_model=list[BookOut])
def list_books(service: BookService = Depends(get_book_service)) -> list[Book]:
    return service.list_books()
