"""Auth request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    full_name: str = Field(..., max_length=255)
    mobile: str = Field(..., min_length=10, max_length=15)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    identifier: str = Field(
        ...,
        description="Mobile number or email address",
    )
    password: str = Field(..., min_length=6)


class CreateUnitRequest(BaseModel):
    community_code: str = Field(..., max_length=20)
    block: str = Field(None, max_length=50)
    flat_number: str = Field(..., max_length=50)
    floor: str = Field(None, max_length=50)


class UnitResponse(BaseModel):
    message: str
    unit_id: int
    community_id: int


class CreateUnitMemberRequest(BaseModel):
    user_id: int
    unit_id: int
    community_id: int
    role: str = Field(..., max_length=50)
    status: bool = Field(default=False)


class UnitMemberResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    mobile: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SignupResponse(BaseModel):
    message: str
    user_id: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
