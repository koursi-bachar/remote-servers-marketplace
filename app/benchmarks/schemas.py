from uuid import UUID
from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional


class BenchmarkCreate(BaseModel):
    name: str
    score: str
    methodology_uri: Optional[HttpUrl] = None
    artifact_uri: Optional[HttpUrl] = None
    listing_id: Optional[UUID] = None

class BenchmarkRead(BaseModel):
    id: UUID
    machine_id: UUID
    listing_id: Optional[UUID]
    name: str
    score: str
    methodology_uri: Optional[str]
    artifact_uri: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)