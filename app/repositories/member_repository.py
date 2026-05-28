from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Member


class MemberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **fields) -> Member:
        member = Member(**fields)
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def get(self, member_id: int) -> Member | None:
        return await self.db.get(Member, member_id)

    async def get_by_email(self, email: str) -> Member | None:
        return await self.db.scalar(
            select(Member).where(func.lower(func.trim(Member.email)) == email)
        )

    async def list_all(self) -> list[Member]:
        result = await self.db.scalars(select(Member).order_by(Member.id))
        return list(result)

    async def save(self, member: Member) -> Member:
        await self.db.commit()
        await self.db.refresh(member)
        return member
