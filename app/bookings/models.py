from sqlalchemy import Column, Float, DateTime, ForeignKey, Enum as SQLEnum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum
import uuid

from app.database import Base
from datetime import datetime, timezone


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Booking(Base):
    
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    buyer_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    listing_id = Column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Nullable to allow individual buyers to create bookings 
    organization_id = Column(  
        UUID(as_uuid=True),  
        ForeignKey("organizations.id", ondelete="SET NULL"),  
        nullable=True,  
        index=True,  
    )

    # Booking window
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    # These track actual usage window 
    active_session_start = Column(DateTime(timezone=True), nullable=True)
    active_session_end = Column(DateTime(timezone=True), nullable=True)

    total_price_estimate = Column(
        Numeric(precision=10, scale=2),
        nullable=False
    )

    actual_price_charged = Column(
        Numeric(precision=10, scale=2), 
        nullable=True
        )

    usage_seconds = Column(Numeric(precision=10, scale=2), nullable=True)
    currency = Column(String(length=3), nullable=False, default="USD")

    status = Column(
        SQLEnum(BookingStatus, name="bookingstatus", native_enum=False),
        nullable=False,
        default=BookingStatus.REQUESTED,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    listing = relationship("Listing", back_populates="bookings")
    buyer = relationship("User", back_populates="bookings")
    organization = relationship("Organization", back_populates="bookings")

    access_credentials = relationship(
        "AccessCredential",
        back_populates="booking",
        cascade="all, delete-orphan"
    )

    wipe_attestation = relationship(
        "WipeAttestation", 
        back_populates="booking", 
        uselist=False,
        cascade="all, delete-orphan"
    )

    payments = relationship(
        "Payment",
        back_populates="booking",
        cascade="all, delete-orphan"
    )

    disputes = relationship(
        "Dispute",
        back_populates="booking",
        cascade="all, delete-orphan"
    )

    """Computed fields for API responses."""
    @property
    def listing_title(self):
        return self.listing.title if self.listing else None

    @property
    def buyer_email(self):
        return self.buyer.email if self.buyer else None