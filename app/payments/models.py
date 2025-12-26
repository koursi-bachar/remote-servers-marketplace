from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Enum as SQLEnum
from enum import Enum
import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PaymentType(str, Enum):
    ESCROW = "escrow"
    CAPTURE = "capture"
    REFUND = "refund"

class PaymentStatus(str, Enum):
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Payment(Base):
    """
    Payment domain model.
    """
    __tablename__ = "payments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = Column(
        SQLEnum(PaymentType, name="payment_type_enum"),
        nullable=False,
    )

    processor_ref = Column(
        String,
        nullable=False,
        doc="Reference returned by the payment processor (e.g., Stripe PaymentIntent ID)",
    )

    amount = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
        doc="The amount associated with this payment operation",
    )

    currency = Column(
        String(3),
        nullable=False,
        default="USD",
    )

    status = Column(
        SQLEnum(PaymentStatus, name="payment_status_enum"),
        nullable=False,
        default=PaymentStatus.AUTHORIZED,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    booking = relationship("Booking", back_populates="payments")