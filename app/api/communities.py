"""Community endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.community_repository import CommunityRepository
from app.schemas.community_schema import CommunityCreate, CommunityResponse, CommunityUpdate
from app.services.community_service import CommunityService

router = APIRouter(prefix="/communities", tags=["communities"])


def get_community_service(
    db: AsyncSession = Depends(get_db),
) -> CommunityService:
    return CommunityService(repo=CommunityRepository(db))


@router.post(
    "",
    response_model=CommunityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_community(
    payload: CommunityCreate,
    service: CommunityService = Depends(get_community_service),
):
    try:
        return await service.create_community(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[CommunityResponse])
async def list_communities(
    service: CommunityService = Depends(get_community_service),
):
    return await service.list_communities()


@router.get("/{community_id}", response_model=CommunityResponse)
async def get_community(
    community_id: int,
    service: CommunityService = Depends(get_community_service),
):
    community = await service.get_community(community_id)
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )
    return community


@router.patch("/{community_id}", response_model=CommunityResponse)
async def update_community(
    community_id: int,
    payload: CommunityUpdate,
    service: CommunityService = Depends(get_community_service),
):
    try:
        return await service.update_community(community_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{community_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_community(
    community_id: int,
    service: CommunityService = Depends(get_community_service),
):
    try:
        await service.delete_community(community_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
