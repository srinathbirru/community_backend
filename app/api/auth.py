"""Auth endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.community_repository import CommunityRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    AddProfileRequest,
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UserProfileResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(
        repo=UserRepository(db),
        community_repo=CommunityRepository(db),
        profile_repo=UserProfileRepository(db),
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
        user, token, _ = await service.login(payload.identifier, payload.password)
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


@router.get("/profiles/{user_id}", response_model=list[UserProfileResponse])
async def get_profiles(
    user_id: int,
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_profiles(user_id)


@router.post("/profiles", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def add_profile(
    payload: AddProfileRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.add_profile(
            payload.user_id,
            payload.community_code,
            payload.flat_number,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
