from sqlalchemy import func, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.database import Base


class AccessCredential(Base):
    """
    Issued VPN and SSH credentials for a booking.
    """
    __tablename__ = "access_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vpn_config_uri = Column(String, nullable=False)
    ssh_public_key_fingerprint = Column(String, nullable=False)

    issued_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    revoked_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    booking = relationship("Booking", back_populates="access_credentials")