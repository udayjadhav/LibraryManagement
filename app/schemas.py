from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    description: str | None
    is_borrowed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    active: bool | None = None


class MemberOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BorrowBookRequest(BaseModel):
    member_id: int = Field(gt=0)
    book_id: int = Field(gt=0)


class BorrowingOut(BaseModel):
    id: int
    member_id: int
    book_id: int
    borrowed_at: datetime
    returned_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
