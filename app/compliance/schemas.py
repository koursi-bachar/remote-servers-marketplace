from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict


class WipeReviewStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class WipeAttestationRead(BaseModel):
    id: UUID
    booking_id: UUID
    machine_id: UUID
    method: str
    evidence_uri: str | None
    attested_at: datetime
    status: WipeReviewStatus

    model_config = ConfigDict(from_attributes=True)

# For creating attestations (used by simulate_wipe)
class WipeAttestationCreate(BaseModel):
    booking_id: UUID
    machine_id: UUID
    method: str
    evidence_uri: str | None = None

# For updating status (admin review)
class WipeAttestationUpdateStatus(BaseModel):
    status: WipeReviewStatus

#Public response
class WipeAttestationPublic(BaseModel):
    id: UUID
    booking_id: UUID
    machine_id: UUID
    method: str
    evidence_uri: str | None
    attested_at: datetime
    status: WipeReviewStatus

    model_config = ConfigDict(from_attributes=True)

#Buyer-facing minimal verification
class WipeVerificationPublic(BaseModel):
    is_verified: bool
    status: WipeReviewStatus | None
    verified_at: datetime | None
    method_summary: str
    
    model_config = ConfigDict(from_attributes=True)