from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from enum import Enum


class OrgStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"

class OrgRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

class OrganizationCreate(BaseModel):
    name: str
    billing_email: EmailStr

class OrganizationUpdate(BaseModel):
    name: str | None = None
    billing_email: EmailStr | None = None
    status: OrgStatus | None = None

class OrganizationRead(BaseModel):
    id: UUID
    name: str
    billing_email: EmailStr
    status: OrgStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MembershipCreate(BaseModel):
    user_id: UUID
    role: OrgRole

class MembershipRead(BaseModel):
    id: UUID
    user_id: UUID
    org_role: OrgRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MembershipUpdateRole(BaseModel):
    role: OrgRole