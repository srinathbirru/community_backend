"""Unit SQLAlchemy model."""

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    community_code: Mapped[str] = mapped_column(String(20), nullable=False)
    block: Mapped[str] = mapped_column(String(50), nullable=True)
    flat_number: Mapped[str] = mapped_column(String(50), nullable=False)
    floor: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
