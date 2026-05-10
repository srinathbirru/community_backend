"""UserProfile data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile


class UserProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> list[UserProfile]:
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_user_id_community_flat(
        self, user_id: int, community_code: str, flat_number: str
    ) -> UserProfile | None:
        result = await self.db.execute(
            select(UserProfile).where(
                UserProfile.user_id == user_id,
                UserProfile.community_code == community_code,
                UserProfile.flat_number == flat_number,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, profile: UserProfile) -> UserProfile:
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
