"""Community business logic."""

from app.models.community import Community
from app.repositories.community_repository import CommunityRepository
from app.schemas.community_schema import CommunityCreate, CommunityUpdate


class CommunityService:
    def __init__(self, repo: CommunityRepository):
        self.repo = repo

    def _generate_code(self, name: str, community_id: int) -> str:
        """Generate a community code: first 3 letters of name + zero-padded 4-digit ID."""
        prefix = name.replace(" ", "")[:3].upper()
        # Pad with 'X' if name is shorter than 3 characters
        prefix = prefix.ljust(3, "X")
        return f"{prefix}{community_id:04d}"

    async def create_community(self, payload: CommunityCreate) -> Community:
        # Step 1: Save with a placeholder code to obtain the auto-increment ID
        community = Community(
            name=payload.name,
            code="TEMP",
            address=payload.address,
            city=payload.city,
            state=payload.state,
            country=payload.country,
        )
        community = await self.repo.create(community)

        # Step 2: Generate the final code from the now-known ID
        community.code = self._generate_code(payload.name, community.id)

        # Step 3: Update with the real code
        return await self.repo.update(community)

    async def get_community(self, community_id: int) -> Community | None:
        return await self.repo.get_by_id(community_id)

    async def list_communities(self) -> list[Community]:
        return list(await self.repo.list_all())

    async def update_community(
        self, community_id: int, payload: CommunityUpdate
    ) -> Community:
        community = await self.repo.get_by_id(community_id)
        if not community:
            raise ValueError("Community not found")

        for field, value in payload.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(community, field, value)

        return await self.repo.update(community)

    async def delete_community(self, community_id: int) -> None:
        community = await self.repo.get_by_id(community_id)
        if not community:
            raise ValueError("Community not found")
        await self.repo.delete(community)
