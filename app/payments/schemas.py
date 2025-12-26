from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

from .models import PaymentType, PaymentStatus

#Base schema (shared fields)
class PaymentBase(BaseModel):
    booking_id: Optional[UUID] = None
    type: Optional[PaymentType] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    processor_ref: Optional[str] = None

#Create schema (input)
class PaymentCreate(PaymentBase):
    """Not exposed publicly to clients."""
    pass

#Public read schema (output)
class PaymentRead(BaseModel):
    id: UUID
    booking_id: UUID
    type: PaymentType
    amount: Decimal
    currency: str
    status: PaymentStatus
    processor_ref: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CheckoutRequest(BaseModel):
    booking_id: UUID
    amount: float
    currency: str = "USD"