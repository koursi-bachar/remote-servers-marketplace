import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict
from app.disputes.models import DisputeStatus


class DisputeBase(BaseModel):
    reason: str = Field(..., description="Description of the dispute reason")

class DisputeCreate(BaseModel):
    booking_id: uuid.UUID = Field(..., description="Booking that the dispute refers to")
    reason: str = Field(..., description="User-provided reason for opening the dispute")

class DisputeResolution(BaseModel):
    """
    Schema used by admins to resolve a dispute.
    - decision: refund | deny
    - refund_amount: required only when decision=refund
    """
    decision: Literal["refund", "deny"]
    refund_amount: Optional[Decimal] = Field(
        None,
        description="Refund amount issued to the buyer (only for refund decisions)"
    )
    resolution_notes: Optional[str] = Field(
        None,
        description="Admin notes explaining the resolution"
    )

class DisputeRead(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    opened_by_user_id: uuid.UUID
    reason: str
    status: DisputeStatus
    resolution_notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class DisputeListItem(BaseModel):
    """A lightweight representation used for list views"""
    id: uuid.UUID
    booking_id: uuid.UUID
    status: DisputeStatus
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)