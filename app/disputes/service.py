import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session

from fastapi import Depends
from app.database import get_db

from .models import DisputeStatus
from .repository import DisputesRepository

from app.bookings.public import BookingsPublic
from app.payments.public import PaymentsPublic

from .schemas import DisputeCreate, DisputeResolution

from app.bookings.public import get_bookings_public
from app.payments.public import get_payments_public

from app.notifications.public import NotificationsPublic, get_notifications_public

class DisputesService:
    """
    Orchestrates the dispute lifecycle:
    - Open dispute (buyers or providers)
    - Transition statuses (admin)
    - Resolve dispute (admin)
    - Trigger refunds via PaymentsPublic
    - Validate booking ownership via BookingsPublic
    """
    def __init__(
        self,
        db: Session,
        repo: DisputesRepository,
        bookings_public: BookingsPublic,
        payments_public: PaymentsPublic,
        notifications_public: NotificationsPublic,
    ):
        self.db = db
        self.repo = repo
        self.bookings_public = bookings_public
        self.payments_public = payments_public
        self.notifications = notifications_public

    def _get_dispute_or_raise(self, dispute_id: uuid.UUID):
        """Gets a dispute if it exists, raises error if it doesn't"""
        dispute = self.repo.get_by_id(self.db, dispute_id)
        if not dispute:
            raise ValueError("Dispute not found")
        return dispute

    def _get_booking_or_raise(self, booking_id: uuid.UUID):
        """Gets a booking if it exists, raises error if it doesn't"""
        booking = self.bookings_public.get_booking(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        return booking

    def _validate_booking_access(self, booking, user_id: uuid.UUID):
        """Determines whether user may open a dispute for a given booking."""
        if booking.buyer_user_id == user_id:
            return True

        machine = booking.listing.machine
        if machine and machine.provider_id == user_id:
            return True

        raise ValueError("User not authorized to dispute this booking")

    def _validate_unique_open_dispute(self, booking_id: uuid.UUID):
        """Verifies a given booking doesn't already have a open dispute"""
        existing = self.repo.list_for_booking(self.db, booking_id)
        for d in existing:
            if d.status in {
                DisputeStatus.OPEN,
                DisputeStatus.IN_REVIEW,
                DisputeStatus.NEEDS_INFO,
            }:
                raise ValueError("An open dispute already exists for this booking")

    def open_dispute(self, user_id: uuid.UUID, payload: DisputeCreate):
        """
        Buyers and providers may open disputes on a booking they own.
        """
        booking = self._get_booking_or_raise(payload.booking_id)
        self._validate_booking_access(booking, user_id)
        self._validate_unique_open_dispute(payload.booking_id)

        dispute = self.repo.create_dispute(
            self.db,
            booking_id=payload.booking_id,
            user_id=user_id,
            reason=payload.reason,
        )

        self.notifications.dispute_opened(dispute, user_id)

        return dispute

    def list_disputes_for_user(self, user_id: uuid.UUID):
        """
        User should see all disputes they opened.
        """
        return self.repo.list_for_user(self.db, user_id)

    def list_disputes_for_booking(self, booking_id: uuid.UUID):
        return self.repo.list_for_booking(self.db, booking_id)

    def list_open_for_admin(self):
        return self.repo.list_open_for_admin(self.db)

    def set_status(
        self,
        dispute_id: uuid.UUID,
        *,
        new_status: DisputeStatus,
        resolution_notes: Optional[str] = None
    ):
        """
        Admin-only status transitions.
        Only certain transitions are allowed.
        """
        dispute = self._get_dispute_or_raise(dispute_id)

        allowed = {
            (DisputeStatus.OPEN, DisputeStatus.IN_REVIEW),
            (DisputeStatus.IN_REVIEW, DisputeStatus.NEEDS_INFO),
            (DisputeStatus.NEEDS_INFO, DisputeStatus.IN_REVIEW),
        }

        if (dispute.status, new_status) not in allowed:
            raise ValueError("Invalid dispute status transition")

        updated = self.repo.update_status(
            self.db,
            dispute_id,
            new_status,
            resolution_notes=resolution_notes,
            resolved_at=None,
        )
        return updated

    def resolve_dispute(
        self,
        dispute_id: uuid.UUID,
        payload: DisputeResolution,
    ):
        dispute = self._get_dispute_or_raise(dispute_id)

        if dispute.status not in {
            DisputeStatus.OPEN,
            DisputeStatus.IN_REVIEW,
            DisputeStatus.NEEDS_INFO,
        }:
            raise ValueError("Dispute must be in-review or needs-info to be resolved")

        booking = self._get_booking_or_raise(dispute.booking_id)

        now = datetime.now(timezone.utc)

        if payload.decision == "refund":
            if payload.refund_amount is None or payload.refund_amount <= 0:
                raise ValueError("refund_amount must be > 0 for refund decisions")

            self.payments_public.refund_for_booking(
                booking_id=booking.id,
                reason="dispute_resolution",
            )

            updated = self.repo.update_status(
                self.db,
                dispute_id,
                DisputeStatus.RESOLVED_REFUNDED,
                resolution_notes=payload.resolution_notes,
                resolved_at=now,
            )

            self.notifications.dispute_resolved(dispute, dispute.user)
            
            return updated

        elif payload.decision == "deny":
            updated = self.repo.update_status(
                self.db,
                dispute_id,
                DisputeStatus.RESOLVED_DENIED,
                resolution_notes=payload.resolution_notes,
                resolved_at=now,
            )

            self.notifications.dispute_resolved(dispute, dispute.user)
            
            return updated

        else:
            raise ValueError("Unsupported decision type")

    def close_dispute(self, dispute_id: uuid.UUID):
        """
        Admin-only. Closes a dispute after it has been resolved.
        """
        dispute = self._get_dispute_or_raise(dispute_id)

        if dispute.status not in {
            DisputeStatus.RESOLVED_REFUNDED,
            DisputeStatus.RESOLVED_DENIED,
        }:
            raise ValueError("Only resolved disputes can be closed")

        updated = self.repo.update_status(
            self.db,
            dispute_id,
            DisputeStatus.CLOSED,
            resolution_notes=dispute.resolution_notes,
            resolved_at=dispute.resolved_at,
        )
        return updated
    
    def list_all_for_admin(self):
        """Return ALL disputes for admin dashboard (including resolved/closed)"""
        return self.repo.list_all_for_admin(self.db)

def get_disputes_service(
    db: Session = Depends(get_db),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
    payments_public: PaymentsPublic = Depends(get_payments_public),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> DisputesService:
    repo = DisputesRepository()
    return DisputesService(
        db=db,
        repo=repo,
        bookings_public=bookings_public,
        payments_public=payments_public,
        notifications_public=notifications_public,
    )