import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.disputes.models import Dispute, DisputeStatus


class DisputesRepository:
    
    def create_dispute(
        self,
        db: Session,
        booking_id: uuid.UUID,
        user_id: uuid.UUID,
        reason: str
    ) -> Dispute:
        dispute = Dispute(
            booking_id=booking_id,
            opened_by_user_id=user_id,
            reason=reason,
            status=DisputeStatus.OPEN,
        )
        db.add(dispute)
        db.commit()
        db.refresh(dispute)
        return dispute

    def get_by_id(self, db: Session, dispute_id: uuid.UUID) -> Optional[Dispute]:
        stmt = select(Dispute).where(Dispute.id == dispute_id)
        return db.scalar(stmt)

    def list_for_user(self, db: Session, user_id: uuid.UUID) -> List[Dispute]:
        """
        Returns all disputes opened by the user
        """
        stmt = (
            select(Dispute)
            .where(Dispute.opened_by_user_id == user_id)
            .order_by(Dispute.created_at.desc())
        )
        return list(db.scalars(stmt))

    def list_for_booking(self, db: Session, booking_id: uuid.UUID) -> List[Dispute]:
        stmt = (
            select(Dispute)
            .where(Dispute.booking_id == booking_id)
            .order_by(Dispute.created_at.desc())
        )
        return list(db.scalars(stmt))

    def list_open_for_admin(self, db: Session) -> List[Dispute]:
        stmt = (
            select(Dispute)
            .where(
                Dispute.status.in_(
                    [
                        DisputeStatus.OPEN,
                        DisputeStatus.IN_REVIEW,
                        DisputeStatus.NEEDS_INFO,
                    ]
                )
            )
            .order_by(Dispute.created_at.asc())
        )
        return list(db.scalars(stmt))

    def update_status(
        self,
        db: Session,
        dispute_id: uuid.UUID,
        new_status: DisputeStatus,
        resolution_notes: Optional[str] = None,
        resolved_at: Optional[datetime] = None,
    ) -> Optional[Dispute]:
        stmt = (
            update(Dispute)
            .where(Dispute.id == dispute_id)
            .values(
                status=new_status,
                resolution_notes=resolution_notes,
                resolved_at=resolved_at,
            )
            .execution_options(synchronize_session="fetch")
        )

        db.execute(stmt)
        db.commit()

        return self.get_by_id(db, dispute_id)
    
    def list_all_for_admin(self, db: Session) -> List[Dispute]:
        """Return all disputes for admin dashboard"""
        stmt = (
            select(Dispute)
            .order_by(Dispute.created_at.desc())
        )
        return list(db.scalars(stmt))
