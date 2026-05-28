from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Book, Borrowing, Member
from app.schemas import (
    BookCreate,
    BookOut,
    BookUpdate,
    BorrowBookRequest,
    BorrowingOut,
    MemberCreate,
    MemberOut,
    MemberUpdate,
)

VALIDATION_ERROR = {422: {"description": "Request validation failed (invalid body or query params)"}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Neighborhood Library API", version="1.0.0", lifespan=lifespan)
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dir), name="assets")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    return FileResponse(index_file)


@app.post(
    "/books",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    responses=VALIDATION_ERROR,
)
def create_book(payload: BookCreate, db: Session = Depends(get_db)) -> Book:
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.put(
    "/books/{book_id}",
    response_model=BookOut,
    responses={404: {"description": "Book not found"}, **VALIDATION_ERROR},
)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)) -> Book:
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


@app.get("/books", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)) -> list[Book]:
    return list(db.scalars(select(Book).order_by(Book.id)))


@app.post(
    "/members",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Member email already exists"}, **VALIDATION_ERROR},
)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)) -> Member:
    existing = db.scalar(select(Member).where(Member.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Member email already exists")

    member = Member(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@app.put(
    "/members/{member_id}",
    response_model=MemberOut,
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Member email already exists"},
        **VALIDATION_ERROR,
    },
)
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)) -> Member:
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    updated_fields = payload.model_dump(exclude_unset=True)
    if "email" in updated_fields and updated_fields["email"] != member.email:
        clash = db.scalar(select(Member).where(Member.email == updated_fields["email"]))
        if clash:
            raise HTTPException(status_code=409, detail="Member email already exists")

    for key, value in updated_fields.items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)
    return member


@app.get("/members", response_model=list[MemberOut])
def list_members(db: Session = Depends(get_db)) -> list[Member]:
    return list(db.scalars(select(Member).order_by(Member.id)))


@app.post(
    "/borrowings/borrow",
    response_model=BorrowingOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Inactive member cannot borrow books"},
        404: {"description": "Member or book not found"},
        409: {"description": "Book is already borrowed"},
        **VALIDATION_ERROR,
    },
)
def borrow_book(payload: BorrowBookRequest, db: Session = Depends(get_db)) -> Borrowing:
    member = db.get(Member, payload.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if not member.active:
        raise HTTPException(status_code=400, detail="Inactive member cannot borrow books")

    book = db.get(Book, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    active_borrowing = db.scalar(
        select(Borrowing).where(Borrowing.book_id == book.id, Borrowing.returned_at.is_(None))
    )
    if book.is_borrowed or active_borrowing:
        raise HTTPException(status_code=409, detail="Book is already borrowed")

    borrowing = Borrowing(member_id=member.id, book_id=book.id)
    book.is_borrowed = True
    db.add(borrowing)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Book is already borrowed")
    db.refresh(borrowing)
    return borrowing


@app.post(
    "/borrowings/{borrowing_id}/return",
    response_model=BorrowingOut,
    responses={
        404: {"description": "Borrowing record not found"},
        409: {"description": "Book already returned"},
    },
)
def return_book(borrowing_id: int, db: Session = Depends(get_db)) -> Borrowing:
    borrowing = db.get(Borrowing, borrowing_id)
    if not borrowing:
        raise HTTPException(status_code=404, detail="Borrowing record not found")
    if borrowing.returned_at is not None:
        raise HTTPException(status_code=409, detail="Book already returned")

    borrowing.returned_at = datetime.now(timezone.utc)
    still_active = db.scalar(
        select(Borrowing).where(
            Borrowing.book_id == borrowing.book_id,
            Borrowing.returned_at.is_(None),
            Borrowing.id != borrowing.id,
        )
    )
    borrowing.book.is_borrowed = still_active is not None
    db.commit()
    db.refresh(borrowing)
    return borrowing


@app.get("/borrowings", response_model=list[BorrowingOut])
def list_borrowings(
    member_id: int | None = Query(default=None),
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> list[Borrowing]:
    statement: Select[tuple[Borrowing]] = select(Borrowing).order_by(Borrowing.id)
    if member_id is not None:
        statement = statement.where(Borrowing.member_id == member_id)
    if active_only:
        statement = statement.where(Borrowing.returned_at.is_(None))
    return list(db.scalars(statement))
