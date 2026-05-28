from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Member


class MemberRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, **fields) -> Member:
        member = Member(**fields)
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def get(self, member_id: int) -> Member | None:
        return self.db.get(Member, member_id)

    def get_by_email(self, email: str) -> Member | None:
        return self.db.scalar(
            select(Member).where(func.lower(func.trim(Member.email)) == email)
        )

    def list_all(self) -> list[Member]:
        return list(self.db.scalars(select(Member).order_by(Member.id)))

    def save(self, member: Member) -> Member:
        self.db.commit()
        self.db.refresh(member)
        return member
