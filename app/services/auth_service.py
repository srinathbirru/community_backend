"""Auth business logic."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings
from app.models.user import User
from app.models.user_profile import UserProfile
from app.repositories.community_repository import CommunityRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    SignupRequest,
    SignupResponse,
    UserProfileResponse,
    UserResponse,
)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class AuthService:
    def __init__(
        self,
        repo: UserRepository,
        community_repo: CommunityRepository,
        profile_repo: UserProfileRepository,
    ):
        self.repo = repo
        self.community_repo = community_repo
        self.profile_repo = profile_repo

    def _build_user_response(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def signup(self, payload: SignupRequest) -> SignupResponse:
        existing_user = await self.repo.get_by_mobile_or_email(payload.mobile)
        if existing_user:
            if not verify_password(payload.password, existing_user.password_hash):
                raise ValueError("User already exists with different credentials")

            profiles = await self.profile_repo.get_by_user_id(existing_user.id)
            token = create_access_token(existing_user.id)
            return SignupResponse(
                user_exists=True,
                message="User already exists",
                access_token=token,
                token_type="bearer",
                user=self._build_user_response(existing_user),
                profiles=[UserProfileResponse.model_validate(p) for p in profiles],
            )

        community = await self.community_repo.get_by_code(payload.community_code)
        if not community:
            raise ValueError("community not found")

        user = User(
            full_name=payload.full_name,
            mobile=payload.mobile,
            email=payload.email,
            password_hash=hash_password(payload.password),
            community_code=payload.community_code,
            flat_number=payload.flat_number,
        )
        user = await self.repo.create(user)

        profile = UserProfile(
            user_id=user.id,
            community_code=payload.community_code,
            flat_number=payload.flat_number,
        )
        await self.profile_repo.create(profile)

        token = create_access_token(user.id)
        return SignupResponse(
            user_exists=False,
            message="Signup successful",
            access_token=token,
            token_type="bearer",
            user=self._build_user_response(user),
            profiles=[UserProfileResponse.model_validate(profile)],
        )

    async def login(self, identifier: str, password: str) -> tuple[User, str, list[UserProfile]]:
        user = await self.repo.get_by_mobile_or_email(identifier)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        token = create_access_token(user.id)
        profiles = await self.profile_repo.get_by_user_id(user.id)
        return user, token, profiles

    async def add_profile(
        self, user_id: int, community_code: str, flat_number: str
    ) -> UserProfile:
        community = await self.community_repo.get_by_code(community_code)
        if not community:
            raise ValueError("community not found")

        existing = await self.profile_repo.get_by_user_id_community_flat(
            user_id, community_code, flat_number
        )
        if existing:
            raise ValueError("Profile already exists")

        profile = UserProfile(
            user_id=user_id,
            community_code=community_code,
            flat_number=flat_number,
        )
        return await self.profile_repo.create(profile)

    async def get_profiles(self, user_id: int) -> list[UserProfile]:
        return await self.profile_repo.get_by_user_id(user_id)
