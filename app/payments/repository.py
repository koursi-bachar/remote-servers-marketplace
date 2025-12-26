from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session

from .models import Payment, PaymentType, PaymentStatus


class PaymentsRepository:
    
    def create_payment(self, db: Session, payment: Payment) -> Payment:
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def update_payment(self, db: Session, payment: Payment) -> Payment:
        db.commit()
        db.refresh(payment)
        return payment

    def get_payment_by_id(self, db: Session, payment_id: UUID) -> Optional[Payment]:
        return db.get(Payment, payment_id)

    def list_payments_for_booking(self, db: Session, booking_id: UUID) -> List[Payment]:
        """Returns all payments for a given booking, ordered chronologically."""
        return (
            db.query(Payment)
            .filter(Payment.booking_id == booking_id)
            .order_by(Payment.created_at.asc())
            .all()
        )

    def get_latest_escrow(self, db: Session, booking_id: UUID) -> Optional[Payment]:
        """
        Retrieve the most recent escrow payment for a booking.
        Used before capture() or refund().
        """
        return (
            db.query(Payment)
            .filter(
                Payment.booking_id == booking_id,
                Payment.type == PaymentType.ESCROW
            )
            .order_by(Payment.created_at.desc())
            .first()
        )

    def get_by_processor_ref(self, db: Session, processor_ref: str) -> Optional[Payment]:
        """
        For webhook reconciliation: find a Payment by processor reference.
        """
        return (
            db.query(Payment)
            .filter(Payment.processor_ref == processor_ref)
            .first()
        )
    
    def list_payments_for_bookings(self, db: Session, booking_ids: list[UUID]):
        if not booking_ids:
            return []

        return (
            db.query(Payment)
            .filter(Payment.booking_id.in_(booking_ids))
            .order_by(Payment.created_at.asc())
            .all()
        )

    def get_captured_escrow_payment(self, db: Session, booking_id: UUID) -> Optional[Payment]:
        """Get captured escrow payment for a booking."""
        return (
            db.query(Payment)
            .filter(
                Payment.booking_id == booking_id,
                Payment.type == PaymentType.ESCROW,
                Payment.status == PaymentStatus.CAPTURED
            )
            .first()
        )