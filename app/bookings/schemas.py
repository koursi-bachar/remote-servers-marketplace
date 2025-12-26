from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from enum import Enum

from app.listings.schemas import ListingRead


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BookingAdminCreate(BaseModel):
    """
    Includes buyer_user_id because admins
    assign the target buyer explicitly.
    """
    listing_id: UUID
    start_time: datetime
    end_time: datetime
    buyer_user_id: UUID
    organization_id: Optional[UUID] = None

class BookingRequest(BaseModel):
    listing_id: UUID
    start_time: datetime
    end_time: datetime
    organization_id: Optional[UUID] = None
    
    @field_validator('start_time', 'end_time', mode='after')
    @classmethod
    def ensure_timezone_aware(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware (assume UTC if naive)"""
        if v.tzinfo is None:
            # Assume UTC if no timezone provided
            return v.replace(tzinfo=timezone.utc)
        return v

class BookingRead(BaseModel):
    id: UUID
    listing_id: UUID
    buyer_user_id: UUID
    organization_id: Optional[UUID] = None
    start_time: datetime
    end_time: datetime
    status: BookingStatus

    total_price_estimate: Optional[float] = None
    active_session_start: Optional[datetime] = None
    active_session_end: Optional[datetime] = None
    actual_price_charged: Optional[float] = None
    usage_seconds: Optional[float] = None

    # These fields map to computed properties from the SQLAlchemy model
    listing_title: Optional[str] = None
    buyer_email: Optional[str] = None
    listing: Optional[ListingRead] = None

    model_config = ConfigDict(from_attributes=True)