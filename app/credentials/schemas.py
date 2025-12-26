from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class AccessCredentialBase(BaseModel):
    booking_id: UUID
    vpn_config_uri: Optional[str] = None
    ssh_public_key_fingerprint: Optional[str] = None

class AccessCredentialCreate(AccessCredentialBase):
    pass

class AccessCredentialRead(AccessCredentialBase):
    id: UUID
    issued_at: datetime
    revoked_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)