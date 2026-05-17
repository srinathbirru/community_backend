"""Auth endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.community_repository import CommunityRepository
from app.repositories.unit_member_repository import UnitMemberRepository
from app.repositories.unit_repository import UnitRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    CreateUnitMemberRequest,
    CreateUnitRequest,
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UnitMemberResponse,
    UnitResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(
        repo=UserRepository(db),
        unit_repo=UnitRepository(db),
        unit_member_repo=UnitMemberRepository(db),
        community_repo=CommunityRepository(db),
    )


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.signup(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        user, token = await service.login(payload.identifier, payload.password)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    payload: CreateUnitRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.create_unit(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/unit-members", response_model=UnitMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_unit_member(
    payload: CreateUnitMemberRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.create_unit_member(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
