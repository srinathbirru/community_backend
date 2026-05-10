"""Community data access layer."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import Community


class CommunityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, community_id: int) -> Community | None:
        result = await self.db.execute(
            select(Community).where(Community.id == community_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Community | None:
        result = await self.db.execute(
            select(Community).where(Community.code == code)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Community]:
        result = await self.db.execute(select(Community))
        return result.scalars().all()

    async def create(self, community: Community) -> Community:
        self.db.add(community)
        await self.db.commit()
        await self.db.refresh(community)
        return community

    async def update(self, community: Community) -> Community:
        await self.db.commit()
        await self.db.refresh(community)
        return community

    async def delete(self, community: Community) -> None:
        await self.db.delete(community)
        await self.db.commit()
