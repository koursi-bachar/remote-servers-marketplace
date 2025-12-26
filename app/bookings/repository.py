from uuid import UUID
from sqlalchemy.orm import Session

from .models import Booking
from app.machines.models import Machine
from app.listings.models import Listing


class BookingsRepository:
    
    def create_booking(self, db: Session, booking: Booking) -> Booking: 
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    def update_booking(self, db: Session, booking: Booking) -> Booking:
        db.commit()
        db.refresh(booking)
        return booking

    def list_bookings(self, db: Session):
        return (
            db.query(Booking)
            .order_by(Booking.created_at.desc())
            .all()
        )

    def list_bookings_for_user(self, db: Session, user_id: UUID):
        return (
            db.query(Booking)
            .filter(Booking.buyer_user_id == user_id)
            .order_by(Booking.start_time.desc())
            .all()
        )

    def list_bookings_for_provider(self, db: Session, provider_id: UUID):
        return (
            db.query(Booking)
            .join(Booking.listing)
            .join(Listing.machine)
            .filter(Machine.provider_id == provider_id)
            .order_by(Booking.start_time.desc())
            .all()
        )

    def get_booking_by_id(self, db: Session, booking_id: UUID) -> Booking | None:
        return db.get(Booking, booking_id)
    
    def list_bookings_for_org_in_period(
        self,
        db: Session,
        org_id: UUID,
        period_start,
        period_end,
    ):
        return (
            db.query(Booking)
            .filter(
                Booking.organization_id == org_id,
                Booking.end_time >= period_start,
                Booking.start_time <= period_end,
            )
            .order_by(Booking.start_time.asc())
            .all()
        )
    
    def list_bookings_for_organization(self, db: Session, org_id: UUID):
        return (
            db.query(Booking)
            .filter(Booking.organization_id == org_id)
            .order_by(Booking.created_at.desc())
            .all()
        )