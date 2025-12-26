from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID

from app.machines.schemas import MachineRead


class ListingCreate(BaseModel):
    """Payload sent when creating a new listing."""
    machine_id: UUID
    title: str = Field(min_length=1)
    description: Optional[str] = Field(None, description="Listing description")
    hourly_price: float = Field(gt=0, description="Price per hour (required)")
    daily_price: Optional[float] = Field(None, gt=0, description="Price per day (optional)")
    monthly_price: Optional[float] = Field(None, gt=0, description="Price per month (optional)")
    currency: Optional[str] = Field("USD", min_length=3, max_length=3)
    cancellation_policy: Optional[str] = Field(None, description="flexible, moderate, strict, custom")
    availability_status: Optional[str] = Field("active", description="draft, active, inactive, sold_out, archived")

class ListingRead(ListingCreate):
    id: UUID
    machine: Optional[MachineRead] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ListingFilter(BaseModel):
    """Schema for filtering listings with machine specifications."""
    # Text search
    q: Optional[str] = Field(None, description="Search in title")
    
    # Price range
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price per hour")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price per hour")
    
    # CPU/GPU filters
    min_cpu_cores: Optional[int] = Field(None, ge=1, description="Minimum CPU cores")
    min_ram_gb: Optional[int] = Field(None, ge=1, description="Minimum RAM in GB")
    min_storage_gb: Optional[int] = Field(None, ge=1, description="Minimum storage in GB")
    
    # GPU filters
    gpu_model: Optional[str] = Field(None, description="GPU model (e.g., 'NVIDIA', 'AMD')")
    min_gpu_count: Optional[int] = Field(None, ge=0, description="Minimum number of GPUs")
    min_vram_gb: Optional[int] = Field(None, ge=0, description="Minimum VRAM per GPU in GB")
    
    # Network filter
    min_network_mbps: Optional[int] = Field(None, ge=1, description="Minimum network bandwidth in Mbps")
    
    # Location filter
    location_region: Optional[str] = Field(None, description="Region (e.g., 'us-east', 'eu-west')")
    
    # CPU model filter
    cpu_model: Optional[str] = Field(None, description="CPU model (e.g., 'Intel', 'AMD')")
    
    # Pagination
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    
    # Sorting
    sort_by: str = Field("created_at", description="Field to sort by: title, price, cpu_cores, ram_gb, storage_gb, created_at")
    sort_order: str = Field("desc", description="Sort order: asc or desc")