"""Auth request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    full_name: str = Field(..., max_length=255)
    mobile: str = Field(..., min_length=10, max_length=15)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    community_code: str = Field(..., max_length=20)
    flat_number: str = Field(..., max_length=50)


class LoginRequest(BaseModel):
    identifier: str = Field(
        ...,
        description="Mobile number or email address",
    )
    password: str = Field(..., min_length=6)


class AddProfileRequest(BaseModel):
    user_id: int
    community_code: str = Field(..., max_length=20)
    flat_number: str = Field(..., max_length=50)


class UserProfileResponse(BaseModel):
    id: int
    community_code: str
    flat_number: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    full_name: str
    mobile: str
    email: str
    community_code: str
    flat_number: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SignupResponse(BaseModel):
    user_exists: bool
    message: str
    access_token: str | None = None
    token_type: str | None = None
    user: UserResponse | None = None
    profiles: list[UserProfileResponse] = []


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
