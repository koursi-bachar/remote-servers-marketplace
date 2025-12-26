from sqlalchemy.orm import Session
from uuid import UUID

from .models import Organization, OrganizationMembership, OrgRole


class OrganizationsRepository:
    
    def create(self, db: Session, data: dict) -> Organization:
        org = Organization(**data)
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    def update(self, db: Session, org: Organization, data: dict) -> Organization:
        for k, v in data.items():
            setattr(org, k, v)
        db.commit()
        db.refresh(org)
        return org

    def get(self, db: Session, org_id: UUID) -> Organization | None:
        return db.query(Organization).filter_by(id=org_id).first()

    def list_for_user(self, db: Session, user_id: UUID):
        return (
            db.query(Organization)
            .join(OrganizationMembership)
            .filter(OrganizationMembership.user_id == user_id)
            .all()
        )

    def add_member(self, db: Session, org_id: UUID, user_id: UUID, role: OrgRole):
        record = OrganizationMembership(
            organization_id=org_id,
            user_id=user_id,
            org_role=role,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def remove_member(self, db: Session, org_id: UUID, user_id: UUID):
        db.query(OrganizationMembership).filter_by(
            organization_id=org_id,
            user_id=user_id
        ).delete()
        db.commit()

    def change_role(self, db: Session, org_id: UUID, user_id: UUID, role: OrgRole):
        membership = (
            db.query(OrganizationMembership)
            .filter_by(organization_id=org_id, user_id=user_id)
            .first()
        )
        membership.org_role = role
        db.commit()
        db.refresh(membership)
        return membership

    def list_members(self, db: Session, org_id: UUID):
        return (
            db.query(OrganizationMembership)
            .filter_by(organization_id=org_id)
            .all()
        )

    def get_membership(self, db: Session, org_id: UUID, user_id: UUID):
        return (
            db.query(OrganizationMembership)
            .filter_by(organization_id=org_id, user_id=user_id)
            .first()
        )