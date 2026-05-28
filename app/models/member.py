from __future__ import annotations

from datetime import datetime, UTC

from sqlalchemy import Boolean, DateTime, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Member(Base):
    __tablename__ = "members"
    __table_args__ = (
        Index(
            "uq_members_email_normalized",
            text("lower(trim(email))"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    borrowings: Mapped[list[Borrowing]] = relationship(
        "Borrowing", back_populates="member"
    )
