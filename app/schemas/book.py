from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
