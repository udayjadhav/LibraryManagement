from __future__ import annotations

from datetime import datetime, UTC

from sqlalchemy import Boolean, DateTime, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        Index(
            "uq_books_title_author_normalized",
            text("lower(trim(title))"),
            text("lower(trim(author))"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_borrowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    borrowings: Mapped[list[Borrowing]] = relationship(
        "Borrowing", back_populates="book"
    )
