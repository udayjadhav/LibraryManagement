from __future__ import annotations

from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Borrowing(Base):
    __tablename__ = "borrowings"
    __table_args__ = (
        Index(
            "uq_active_borrowing_per_book",
            "book_id",
            unique=True,
            sqlite_where=text("returned_at IS NULL"),
            postgresql_where=text("returned_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    member: Mapped[Member] = relationship("Member", back_populates="borrowings")
    book: Mapped[Book] = relationship("Book", back_populates="borrowings")
