from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MetricSample(Base):
    """
    A single time-stamped operational measurement for a machine.
    Append-only: service layer enforces no updates/deletes for historical integrity.
    """
    __tablename__ = "metric_samples"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    recorded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    gpu_util = Column(Float, nullable=True)
    cpu_util = Column(Float, nullable=True)
    mem_used_gb = Column(Float, nullable=True)   #used RAM in GB
    net_rx_mb = Column(Float, nullable=True)     #received MB during window
    net_tx_mb = Column(Float, nullable=True)     #transmitted MB during window

    machine = relationship("Machine", back_populates="metric_samples")