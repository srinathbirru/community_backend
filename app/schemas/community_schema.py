"""Community request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommunityCreate(BaseModel):
    name: str = Field(
        ...,
        max_length=255,
        pattern=r"^[a-zA-Z0-9 ]+$",
    )
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)


class CommunityUpdate(BaseModel):
    name: str | None = Field(
        None,
        max_length=255,
        pattern=r"^[a-zA-Z0-9 ]+$",
    )
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)


class CommunityResponse(BaseModel):
    id: int
    name: str
    code: str
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
