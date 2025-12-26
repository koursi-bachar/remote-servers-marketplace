from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class InvoiceStatus(str, Enum):
    PENDING = "pending"
    FINALIZED = "finalized"
    PAID = "paid"
    VOID = "void"

class InvoiceBase(BaseModel):
    organization_id: UUID
    period_start: datetime
    period_end: datetime
    currency: str = Field("usd", max_length=3)

class InvoiceCreate(InvoiceBase):
    """
    Used by admin/automation to request invoice generation.
    """
    pass

class InvoiceRead(InvoiceBase):
    id: UUID
    total_amount: Decimal
    status: InvoiceStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvoiceListItem(InvoiceRead):
    """Currently same as read; split so you can later trim fields."""
    pass

class InvoiceUpdateStatus(BaseModel):
    status: InvoiceStatus