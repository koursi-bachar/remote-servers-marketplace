from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from enum import Enum


class ProviderVerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class VerificationSubject(str, Enum):
    PROVIDER = "provider"
    MACHINE = "machine"

class ProviderProfileCreate(BaseModel):
    """
    User creates a provider profile for themselves.
    """
    payout_account_ref: str | None = None

class ProviderProfileUpdate(BaseModel):
    """
    User can update payout info or metadata.
    """
    payout_account_ref: str | None = None

class ProviderProfileRead(BaseModel):
    """
    Read model returned in API responses.
    """
    id: UUID
    user_id: UUID
    verification_status: ProviderVerificationStatus
    payout_account_ref: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VerificationCreate(BaseModel):
    """
    End-user or system requests a verification event.
    For provider verification:
        subject_type = "provider"
        subject_id = provider_profile.id
    For machine verification:
        subject_type = "machine"
        subject_id = machine.id
    """
    subject_type: VerificationSubject
    subject_id: UUID
    notes: str | None = None

class VerificationUpdateStatus(BaseModel):
    """
    Admin approves/rejects a verification.
    """
    status: VerificationStatus
    notes: str | None = None

class VerificationRead(BaseModel):
    """
    Returned in API responses (single or list).
    """
    id: UUID
    subject_type: VerificationSubject
    subject_id: UUID
    status: VerificationStatus
    performed_by_admin_id: UUID | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)