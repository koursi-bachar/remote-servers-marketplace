from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select
from uuid import UUID

from .models import WipeAttestation, WipeReviewStatus


class ComplianceRepository:
    
    def create(self, db: Session, *, booking_id: UUID, machine_id: UUID, 
               method: str, evidence_uri: str):

        att = WipeAttestation(
            booking_id=booking_id,
            machine_id=machine_id,
            method=method,
            evidence_uri=evidence_uri,
        )
        db.add(att)
        db.commit()
        db.refresh(att)
        return att
    
    def get_by_booking(self, db: Session, booking_id: UUID):
        stmt = select(WipeAttestation).where(
            WipeAttestation.booking_id == booking_id
        )
        result = db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_booking_with_relations(self, db: Session, booking_id: UUID):
        """
        Get attestation with all necessary relationships pre-loaded.
        Uses selectinload for better performance with nested relationships.
        """
        return db.query(WipeAttestation).options(
            selectinload(WipeAttestation.booking),  # For ownership check
            selectinload(WipeAttestation.machine)   # For provider check
        ).filter_by(booking_id=booking_id).first()

    def list_machine_attestations(self, db: Session, machine_id: UUID):
        stmt = select(WipeAttestation).where(
            WipeAttestation.machine_id == machine_id
        ).order_by(WipeAttestation.attested_at.desc())
        result = db.execute(stmt)
        return result.scalars().all()

    def list_all(self, db: Session):
        stmt = select(WipeAttestation).order_by(WipeAttestation.attested_at.desc())
        result = db.execute(stmt)
        return result.scalars().all()

    def update_status(self, db: Session, attestation_id: UUID, status: WipeReviewStatus):
        stmt = select(WipeAttestation).where(WipeAttestation.id == attestation_id)
        result = db.execute(stmt)
        att = result.scalar_one_or_none()
        
        if not att:
            return None

        att.status = status
        db.commit()
        db.refresh(att)
        return att