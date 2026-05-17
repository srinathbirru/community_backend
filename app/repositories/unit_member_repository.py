"""UnitMember data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unit_member import UnitMember


class UnitMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, unit_member: UnitMember) -> UnitMember:
        self.db.add(unit_member)
        await self.db.commit()
        await self.db.refresh(unit_member)
        return unit_member
