"""Auth business logic."""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
import bcrypt
from jose import jwt
from app.core.config import settings
from app.models.community import Community
from app.models.unit import Unit
from app.models.unit_member import UnitMember
from app.models.user import User
from app.repositories.community_repository import CommunityRepository
from app.repositories.unit_member_repository import UnitMemberRepository
from app.repositories.unit_repository import UnitRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    CreateUnitMemberRequest,
    CreateUnitRequest,
    SignupRequest,
    SignupResponse,
    UnitMemberResponse,
    UnitResponse,
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
        unit_repo: UnitRepository,
        unit_member_repo: UnitMemberRepository,
        community_repo: CommunityRepository,
    ):
        self.repo = repo
        self.unit_repo = unit_repo
        self.unit_member_repo = unit_member_repo
        self.community_repo = community_repo

    def _build_user_response(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def signup(self, payload: SignupRequest) -> SignupResponse:
        existing_user = await self.repo.get_by_mobile_or_email(payload.mobile)
        if existing_user:
            return SignupResponse(
                message="User already exists with this mobile or email.",
                user_id=existing_user.id,
            )

        user = User(
            full_name=payload.full_name,
            mobile=payload.mobile,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        user = await self.repo.create(user)

        return SignupResponse(
            message="User created successfully",
            user_id=user.id,
        )

    async def login(self, identifier: str, password: str) -> tuple[User, str]:
        user = await self.repo.get_by_mobile_or_email(identifier)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        token = create_access_token(user.id)
        return user, token

    async def create_unit(self, payload: CreateUnitRequest) -> UnitResponse:
        # Check if community exists
        community = await self.community_repo.get_by_code(payload.community_code)
        if not community:
            raise ValueError(f"Community with code '{payload.community_code}' does not exist")

        unit = Unit(
            community_code=payload.community_code,
            block=payload.block,
            flat_number=payload.flat_number,
            floor=payload.floor,
        )
        unit = await self.unit_repo.create(unit)
        return UnitResponse(
            message="Unit created successfully",
            unit_id=unit.id,
            community_id=community.id,
        )

    async def create_unit_member(self, payload: CreateUnitMemberRequest) -> UnitMemberResponse:
        # Check if user exists
        user = await self.repo.get_by_id(payload.user_id)
        if not user:
            raise ValueError(f"User with id '{payload.user_id}' does not exist")
            
        # Check if unit exists
        unit = await self.unit_repo.get_by_id(payload.unit_id)
        if not unit:
            raise ValueError(f"Unit with id '{payload.unit_id}' does not exist")

        # Check if community exists
        community = await self.community_repo.get_by_id(payload.community_id)
        if not community:
            raise ValueError(f"Community with id '{payload.community_id}' does not exist")

        unit_member = UnitMember(
            user_id=payload.user_id,
            unit_id=payload.unit_id,
            community_id=payload.community_id,
            role=payload.role,
            status=payload.status,
        )
        await self.unit_member_repo.create(unit_member)
        return UnitMemberResponse(
            message="Unit member created successfully",
        )
