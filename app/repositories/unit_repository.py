"""Unit data access layer."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unit import Unit


class UnitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, unit_id: int) -> Unit | None:
        result = await self.db.execute(
            select(Unit).where(Unit.id == unit_id)
        )
        return result.scalar_one_or_none()

    async def create(self, unit: Unit) -> Unit:
        self.db.add(unit)
        await self.db.commit()
        await self.db.refresh(unit)
        return unit
