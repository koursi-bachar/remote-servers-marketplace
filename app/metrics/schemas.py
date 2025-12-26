from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# Create (ingestion from agent)
class MetricSampleCreate(BaseModel):
    """
    Schema used by ProviderAgentClient to submit one metric sample.
    """
    recorded_at: Optional[datetime] = Field(
        None,
        description="Timestamp when metrics were captured on the machine. "
                    "If not provided, backend will set current time.",
    )

    gpu_util: Optional[float] = Field(
        None, ge=0, le=100, description="GPU utilization percentage"
    )
    cpu_util: Optional[float] = Field(
        None, ge=0, le=100, description="CPU utilization percentage"
    )
    mem_used_gb: Optional[float] = Field(
        None, ge=0, description="Used RAM in GB"
    )
    net_rx_mb: Optional[float] = Field(
        None, ge=0, description="Received MB during sampling interval"
    )
    net_tx_mb: Optional[float] = Field(
        None, ge=0, description="Transmitted MB during sampling interval"
    )

class MetricSampleRead(BaseModel):
    id: UUID
    machine_id: UUID
    recorded_at: datetime

    gpu_util: Optional[float]
    cpu_util: Optional[float]
    mem_used_gb: Optional[float]
    net_rx_mb: Optional[float]
    net_tx_mb: Optional[float]

    model_config = ConfigDict(from_attributes=True)

class MetricSampleListItem(BaseModel):
    """
    Returned in lists.
    Optimized for time-series display.
    """
    recorded_at: datetime
    gpu_util: Optional[float]
    cpu_util: Optional[float]
    mem_used_gb: Optional[float]
    net_rx_mb: Optional[float]
    net_tx_mb: Optional[float]

    model_config = ConfigDict(from_attributes=True)

# Optional query parameters for filtering & windowing.
class MetricsQueryParams(BaseModel):
    start: Optional[datetime] = Field(
        None, description="Return metrics recorded on/after this timestamp"
    )
    end: Optional[datetime] = Field(
        None, description="Return metrics recorded on/before this timestamp"
    )
    limit: Optional[int] = Field(
        None, ge=1, le=5000, description="Maximum number of samples to return"
    )