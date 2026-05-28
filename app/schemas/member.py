from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
