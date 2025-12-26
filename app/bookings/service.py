"""
This service defines how bookings behave, including how they move from PENDING_PAYMENT, to REQUESTED,
to CONFIRMED, become ACTIVE, and then COMPLETE or CANCELLED.

The router calls into this layer whenever the user tries to perform
an action. The repository only reads or writes to the DB. The rules
for what is allowed live here.
"""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session

from .models import Booking
from .schemas import (
    BookingRequest,
    BookingAdminCreate,
    BookingStatus
)

from .repository import BookingsRepository
from app.listings.public import ListingsPublic, get_listings_public

from fastapi import Depends
from app.database import get_db

from uuid import UUID

from app.credentials.public import AccessCredentialsPublic, get_credentials_public
from app.payments.public import PaymentsPublic, get_payments_public
from app.organizations.public import OrganizationsPublic, get_organizations_public
from app.compliance.public import CompliancePublic, get_compliance_public
from app.notifications.public import NotificationsPublic, get_notifications_public


class BookingsService:

    def __init__(
        self,
        db: Session,
        booking_repo: BookingsRepository,
        listings_public: ListingsPublic,
        credentials_public: AccessCredentialsPublic,
        payments_public: PaymentsPublic,
        organizations_public: OrganizationsPublic,
        compliance_public: CompliancePublic,
        notifications_public: NotificationsPublic,
    ):
        self.db = db
        self.booking_repo = booking_repo
        self.listings_public = listings_public
        self.credentials_public = credentials_public
        self.payments_public = payments_public
        self.organizations_public = organizations_public
        self.compliance_public = compliance_public
        self.notifications = notifications_public

    def normalize_times(self, start_time, end_time):
        """
        Convert timezone-aware datetimes to UTC.
        Raises ValueError for naive datetimes.
        """
        if start_time.tzinfo is None or end_time.tzinfo is None:
            raise ValueError("start_time and end_time must be timezone-aware")
    
        start_utc = start_time.astimezone(timezone.utc)
        end_utc = end_time.astimezone(timezone.utc)
        return start_utc, end_utc

    def validate_booking_window(self, start_utc, end_utc):
        """Check that provided start time and end time are provided and sequential"""
        if start_utc is None or end_utc is None:
            raise ValueError("start_time and end_time must be provided.")   

        if end_utc <= start_utc:
            raise ValueError("end_time must be after start_time")  

    def fetch_listing_or_raise(self, listing_id):
        """Get the listing or raise an error if none is found"""
        listing = self.listings_public.get_listing_by_id(listing_id)
        if not listing:
            raise ValueError("Listing not found") 
        return listing

    def calculate_price(self, start_time, end_time, hourly_price):
        """Calculate the price of a booking ensuring decimal data for financial rounding logic"""
        if not isinstance(hourly_price, Decimal):
            hourly_decimal = Decimal(str(hourly_price))
        else:
            hourly_decimal = hourly_price
        if hourly_decimal <= 0:
            raise ValueError("Hourly price must be greater than 0.")  
        delta = end_time - start_time
        total_seconds = Decimal(str(delta.total_seconds()))
        total_price = (total_seconds * hourly_decimal) / Decimal('3600')
        return total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def build_booking_model(self, payload, buyer_user_id, start_utc, end_utc, total_price, organization_id=None):
        """Build the Booking model for passing to the repository"""
        booking = Booking( 
            listing_id=payload.listing_id,
            buyer_user_id=buyer_user_id,
            start_time=start_utc,
            end_time=end_utc,
            total_price_estimate=total_price,
            status=BookingStatus.REQUESTED,
            organization_id=organization_id,
        )
        return booking
    
    def list_bookings_for_user(self, user_id: UUID):
        """List user bookings"""
        return self.booking_repo.list_bookings_for_user(self.db, user_id)

    def list_bookings_for_provider(self, provider_id: UUID):
        """List provider bookings"""
        return self.booking_repo.list_bookings_for_provider(self.db, provider_id)

    def list_all_bookings(self):
        """Admin use only, list all bookings across the business"""
        return self.booking_repo.list_bookings(self.db)

    def _get_booking_or_raise(self, booking_id: UUID) -> Booking:
        """Get a booking or return an error if not possible"""
        booking = self.booking_repo.get_booking_by_id(self.db, booking_id)
        if not booking:
            raise ValueError("Booking not found")
        return booking

    def get_booking_readonly(self, booking_id: UUID):
        """Gets booking object (for routes) to impose booking status changes"""
        return self._get_booking_or_raise(booking_id)

    def admin_create_booking(self, payload: BookingAdminCreate):
        """Check booking creation rules before creating booking"""
        start_utc, end_utc = self.normalize_times(payload.start_time, payload.end_time)
        
        self.validate_booking_window(start_utc, end_utc)
        
        listing = self.fetch_listing_or_raise(payload.listing_id)
        
        total_price = self.calculate_price(start_utc, end_utc, listing.hourly_price)

        booking = self.build_booking_model(
            payload, 
            payload.buyer_user_id,
            start_utc,
            end_utc,
            total_price,
            organization_id=payload.organization_id,
        )
        
        return self.booking_repo.create_booking(self.db, booking)

    def request_booking(self, buyer_user_id, payload: BookingRequest):
        """Check booking creation rules before creating booking"""
        start_utc, end_utc = self.normalize_times(payload.start_time, payload.end_time)
        
        if buyer_user_id is None:
            raise ValueError("buyer_user_id is required")
        
        self.validate_booking_window(start_utc, end_utc)
        
        listing = self.fetch_listing_or_raise(payload.listing_id)

        total_price = self.calculate_price(start_utc, end_utc, listing.hourly_price)

        if payload.organization_id is not None:
            is_admin = self.organizations_public.is_org_admin(buyer_user_id, payload.organization_id)
            if not is_admin:
                raise ValueError("User is not an admin of the specified organization")

        booking = self.build_booking_model(payload, buyer_user_id, start_utc, end_utc, total_price)

        created = self.booking_repo.create_booking(self.db, booking)

        if booking.status != BookingStatus.REQUESTED:
            raise ValueError("Escrow can only be created for requested bookings.")

        #Payments: escrow hold immediately upon booking request
        self.payments_public.escrow_for_booking(
            booking=created,
            amount=created.total_price_estimate,
            currency=created.listing.currency if hasattr(created.listing, "currency") else "USD",
        )

        return created

    def confirm_booking(self, booking_id: UUID, booking: Booking | None = None):
        """
        Providers and admins call this when approving a buyer's request.
        A booking can only be confirmed once. After that point,
        session start and end rules apply.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)

        if booking.listing is None:
            raise ValueError("Cannot confirm a booking without an associated listing")  

        now = datetime.now(timezone.utc)

        if now > booking.end_time:
            raise ValueError("Cannot confirm booking after booking end_time") 
        
        if booking.status != BookingStatus.REQUESTED:
            raise ValueError("Bookings can only be confirmed from a requested state") 
        
        booking.status = BookingStatus.CONFIRMED

        updated = self.booking_repo.update_booking(self.db, booking)

        self.notifications.booking_confirmed(booking.buyer, booking)

        return updated

    def cancel_booking(self, booking_id: UUID, booking: Booking | None = None):
        """
        Booking cancellation is only possible if a booking has not begun
        A booking must be in a PENDING_PAYMENT, REQUESTED, or CONFIRMED state to cancel
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)
        
        if booking.listing is None:
            raise ValueError("Cannot cancel a booking without an associated listing")
        
        now = datetime.now(timezone.utc)
        
        if now > booking.start_time:
            raise ValueError("Cannot cancel booking after booking start_time")
        
        if booking.status not in {BookingStatus.PENDING_PAYMENT, BookingStatus.REQUESTED, BookingStatus.CONFIRMED}:
            raise ValueError("Booking must be pending, requested, or confirmed in order to cancel.")
        
        #Update booking status first
        booking.status = BookingStatus.CANCELLED
        updated = self.booking_repo.update_booking(self.db, booking)
        
        #Notify user
        self.notifications.booking_cancelled(booking.buyer, booking, reason="user_cancelled")
        
        #Void the payment authorization if payment is authorized but not captured
        if booking.status == BookingStatus.CANCELLED:
            try:
                self.payments_public.void_escrow_for_booking(booking=booking)
            except ValueError as e:
                # Log but don't fail if payment can't be voided
                print(f"Warning: Could not void payment for booking {booking_id}: {str(e)}")
        
        return updated

    def start_session(self, booking_id: UUID, booking: Booking | None = None):
        """
        A session can only begin during the reserved window.
        We disallow starting outside it because usage is tied to billing
        and the hosting provider's capacity planning.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)
        
        if not booking.listing:
            raise ValueError("Listing not attached to booking") 

        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError("Only a confirmed booking can be started.") 

        if booking.active_session_start is not None:
            raise ValueError("Session already started") 

        now = datetime.now(timezone.utc)

        if now < booking.start_time:
            raise ValueError("Cannot start before booking start_time") 
        if now > booking.end_time:
            raise ValueError("Cannot start; booking window expired") 

        booking.active_session_start = now
        booking.status = BookingStatus.ACTIVE

        updated = self.booking_repo.update_booking(self.db, booking)

        self.notifications.booking_activated(booking.buyer, booking)

        if booking.status != BookingStatus.ACTIVE:
            raise ValueError("Cannot issue credentials unless booking is ACTIVE.")
        
        self.credentials_public.issue_for_booking(booking)

        return updated

    def end_session(self, booking_id: UUID, booking: Booking | None = None):
        """
        Ends the booking session. Checks for correct current booking status.
        Simulates a sever wipe and credentials revoke, and triggers captured payment.
        Final billing is based on exact session duration.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)
        
        if not booking.listing:
            raise ValueError("Listing not attached to booking")
        
        if booking.status != BookingStatus.ACTIVE:
            raise ValueError("Cannot end, current status is not active")
        
        if booking.active_session_end is not None:
            raise ValueError("Session already ended")
        
        now = datetime.now(timezone.utc)
        booking.active_session_end = now
        
        # Calculate actual price based on exact usage
        booking.actual_price_charged = self.calculate_price(
            booking.active_session_start,
            booking.active_session_end,
            booking.listing.hourly_price
        )
        
        #Compliance steps
        self.compliance_public.simulate_wipe_for_booking(booking)
        self.compliance_public.require_attestation_for_booking(booking)
        
        booking.status = BookingStatus.COMPLETED
        updated = self.booking_repo.update_booking(self.db, booking)
        
        self.notifications.booking_completed(booking.buyer, booking)
        
        #Capture the payment
        try:
            self.payments_public.capture_for_booking(booking=booking)
        except ValueError as e:
            print(f"ERROR: Failed to capture payment for booking {booking_id}: {str(e)}")
        
        #Revoke credentials
        self.credentials_public.revoke_for_booking(booking)
        
        return updated

    def get_org_bookings_in_period(self, org_id, period_start, period_end):
        """
        Thin service wrapper for invoice aggregation.
        Calls repository function only; no cross-domain imports.
        """
        return self.booking_repo.list_bookings_for_org_in_period(
            self.db,
            org_id=org_id,
            period_start=period_start,
            period_end=period_end,
        )

    def create_booking_draft(
        self,
        buyer_user_id,
        payload: BookingRequest
    ):
        """
        Create a booking in "pending_payment" status for Stripe Checkout flow.
        Does NOT create escrow - payment happens separately.
        """
        #Copy all validation from request_booking
        start_utc, end_utc = self.normalize_times(payload.start_time, payload.end_time)
        
        if buyer_user_id is None:
            raise ValueError("buyer_user_id is required")
        
        self.validate_booking_window(start_utc, end_utc)
        
        listing = self.fetch_listing_or_raise(payload.listing_id)
        total_price = self.calculate_price(start_utc, end_utc, listing.hourly_price)

        if payload.organization_id is not None:
            is_admin = self.organizations_public.is_org_admin(buyer_user_id, payload.organization_id)
            if not is_admin:
                raise ValueError("User is not an admin of the specified organization")

        booking = self.build_booking_model(payload, buyer_user_id, start_utc, end_utc, total_price)
        
        booking.status = BookingStatus.PENDING_PAYMENT
        
        created = self.booking_repo.create_booking(self.db, booking)
        
        return created

    def get_bookings_for_organization(self, org_id: UUID):
        """
        Get all bookings for an organization.
        Uses repository method that doesn't require cross-domain imports.
        """
        return self.booking_repo.list_bookings_for_organization(self.db, org_id)

def get_bookings_service(
    db: Session = Depends(get_db),
    listings_public: ListingsPublic = Depends(get_listings_public),
    credentials_public: AccessCredentialsPublic = Depends(get_credentials_public),
    payments_public: PaymentsPublic = Depends(get_payments_public),
    organizations_public: OrganizationsPublic = Depends(get_organizations_public),
    compliance_public: CompliancePublic = Depends(get_compliance_public),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> BookingsService:
    repo = BookingsRepository()
    return BookingsService(
        db=db,
        booking_repo=repo,
        listings_public=listings_public,
        credentials_public=credentials_public,
        payments_public=payments_public,
        organizations_public=organizations_public,
        compliance_public=compliance_public,
        notifications_public=notifications_public,
    )