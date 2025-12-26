from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class MachineCreate(BaseModel):
    provider_id: Optional[UUID] = None
    hostname: str = Field(..., min_length=1, description="Server hostname/identifier")
    location_region: str = Field(..., min_length=1, description="AWS region, data center location, etc.")

    gpu_model: str = Field(..., description="GPU model (e.g., 'NVIDIA A100', 'AMD MI250X')")
    gpu_count: int = Field(..., ge=0, description="Number of GPUs")
    vram_gb: int = Field(..., ge=0, description="VRAM per GPU in GB")

    cpu_model: str = Field(..., description="CPU model (e.g., 'Intel Xeon Platinum 8480C')")
    cpu_cores: int = Field(..., ge=1, description="Total CPU cores")
    ram_gb: int = Field(..., ge=1, description="System RAM in GB")

    storage_gb: int = Field(..., ge=1, description="Storage capacity in GB")
    network_mbps: int = Field(..., ge=1, description="Network bandwidth in Mbps")
    notes: Optional[str] = Field(None, description="Additional notes or description")

class MachineRead(MachineCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)