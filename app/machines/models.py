from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Machine(Base):
    """These are the physical servers offered by providers."""
    __tablename__ = "machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Hardware and descriptive attributes
    hostname = Column(String, nullable=False)
    location_region = Column(String, nullable=False)

    gpu_model = Column(String, nullable=False)
    gpu_count = Column(Integer, nullable=False)
    vram_gb = Column(Integer, nullable=False)

    cpu_model = Column(String, nullable=False)
    cpu_cores = Column(Integer, nullable=False)
    ram_gb = Column(Integer, nullable=False)

    storage_gb = Column(Integer, nullable=False)
    network_mbps = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    provider = relationship("User", back_populates="machines")
    listings = relationship("Listing", back_populates="machine", cascade="all, delete")
    benchmarks = relationship(
        "MachineBenchmark", 
        back_populates="machine",
        cascade="all, delete-orphan"
    )
    wipe_attestations = relationship(
        "WipeAttestation", 
        back_populates="machine",
        cascade="all, delete-orphan"
    )
    metric_samples = relationship(
        "MetricSample",
        back_populates="machine",
        cascade="all, delete-orphan"
    )