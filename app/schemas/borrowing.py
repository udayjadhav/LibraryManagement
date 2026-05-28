from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
