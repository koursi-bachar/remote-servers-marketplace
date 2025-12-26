import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum

from app.database import Base


class WipeReviewStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class WipeAttestation(Base):
    """
    Records attestation that a machine was properly wiped after a booking.
    Includes evidence and review workflow status.
    """
    __tablename__ = "wipe_attestations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    method = Column(String, nullable=False)
    evidence_uri = Column(String, nullable=True)

    attested_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    status = Column(
        SQLEnum(WipeReviewStatus),
        default=WipeReviewStatus.PENDING,
        nullable=False,
    )

    booking = relationship("Booking", back_populates="wipe_attestation", lazy="select")
    machine = relationship("Machine", back_populates="wipe_attestations", lazy="select")