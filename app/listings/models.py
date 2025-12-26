from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Text, func, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ListingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class Listing(Base):
    
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    hourly_price = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
        doc="Price per hour (required)"
    )

    daily_price = Column(
        Numeric(precision=10, scale=2),
        nullable=True,
        doc="Price per day (24 hours) - optional"
    )
    
    monthly_price = Column(
        Numeric(precision=10, scale=2),
        nullable=True,
        doc="Price per month (30 days) - optional"
    )

    currency = Column(String(length=3), nullable=False, default="USD")

    availability_status = Column(
        SQLEnum(ListingStatus, name="listing_status"),
        nullable=False,
        default=ListingStatus.ACTIVE,
    )

    cancellation_policy = Column(
        String(50),
        nullable=True,
        doc="Cancellation policy: flexible, moderate, strict, custom"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    benchmarks = relationship(
        "MachineBenchmark", 
        back_populates="listing",
        cascade="all, delete-orphan"
    )
    
    machine = relationship("Machine", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing", cascade="all, delete")