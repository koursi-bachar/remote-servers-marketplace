import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from enum import Enum


class OrganizationStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"

class OrgRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

class Organization(Base):
    
    __tablename__ = "organizations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String, nullable=False)
    billing_email = Column(String, nullable=False)
    status = Column(
        SQLEnum(OrganizationStatus),
        default=OrganizationStatus.ACTIVE
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    memberships = relationship("OrganizationMembership", back_populates="organization")

    bookings = relationship("Booking", back_populates="organization")
    invoices = relationship(
        "Invoice",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    org_role = Column(SQLEnum(OrgRole), default=OrgRole.MEMBER)

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="organization_memberships")