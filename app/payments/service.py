from uuid import UUID
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from .models import Payment, PaymentType, PaymentStatus
from .repository import PaymentsRepository
from .ports.payment_port import PaymentPort

from app.database import get_db
from fastapi import Depends

from app.providers.public import ProvidersPublic, get_providers_public
from app.notifications.public import NotificationsPublic, get_notifications_public
from .ports.stripe_adapter import get_payment_adapter


class PaymentsService:
    """
    Orchestrates payment flows:
    - Escrow creation (authorization hold)
    - Capture (final charge)
    - Refund (void or refund)
    """
    def __init__(
        self,
        db: Session,
        repo: PaymentsRepository,
        port: PaymentPort,
        providers_public: ProvidersPublic,
        notifications_public: NotificationsPublic,
    ):
        self.db = db
        self.repo = repo
        self.port = port
        self.providers_public = providers_public
        self.notifications = notifications_public

    # Escrow (auth hold)
    def create_escrow(
        self,
        booking,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        """
        Creates an authorization/escrow hold for a booking.
        Called after booking confirmation.
        """
        processor_ref = self.port.create_hold(
            amount=amount,
            currency=currency,
            reference=str(booking.id),
        )

        payment = Payment(
            booking_id=booking.id,
            type=PaymentType.ESCROW,
            amount=amount,
            currency=currency,
            processor_ref=processor_ref,
            status=PaymentStatus.AUTHORIZED,
        )

        return self.repo.create_payment(self.db, payment)

    def void_escrow(self, booking) -> Payment:
        """Void escrow - cancel authorization for uncaptured payments"""
        escrow = self.repo.get_latest_escrow(self.db, booking.id)
        if not escrow:
            raise ValueError("No escrow found to void.")
        
        if escrow.status == PaymentStatus.AUTHORIZED:
            # Use the port abstraction
            self.port.cancel_payment_intent(
                processor_ref=escrow.processor_ref,
            )
            
            # Update local status
            escrow.status = PaymentStatus.CANCELLED
            return self.repo.update_payment(self.db, escrow)
        else:
            raise ValueError(f"Cannot void escrow in status: {escrow.status}. Only AUTHORIZED payments can be voided.")

    def capture(self, booking) -> Payment:
        """Capture the authorized escrow created earlier."""
        escrow = self.repo.get_latest_escrow(self.db, booking.id)
        if not escrow:
            raise ValueError("No escrow found to capture.")
        
        if escrow.status != PaymentStatus.AUTHORIZED:
            raise ValueError("Escrow already captured or refunded.")
        
        self.port.capture(processor_ref=escrow.processor_ref)
        
        # Update local payment state
        escrow.status = PaymentStatus.CAPTURED
        updated = self.repo.update_payment(self.db, escrow)
        
        self.notifications.payment_captured(booking.buyer, updated)
        
        return updated

    def refund(self, booking_id, reason: str | None = None) -> Payment:
        """Refund a captured payment."""
        captured_payment = self.repo.get_captured_escrow_payment(self.db, booking_id)
        
        if not captured_payment:
            raise ValueError("No captured payment found to refund.")
        
        # Use the port abstraction
        self.port.refund(
            processor_ref=captured_payment.processor_ref,
            amount=captured_payment.amount,
        )
        
        # Record refund payment
        refund_payment = Payment(
            booking_id=booking_id,
            type=PaymentType.REFUND,
            amount=captured_payment.amount,
            currency=captured_payment.currency,
            processor_ref=captured_payment.processor_ref, 
            status=PaymentStatus.REFUNDED,
        )
        
        return self.repo.create_payment(self.db, refund_payment)

    # Query
    def list_for_booking(self, booking_id):
        return self.repo.list_payments_for_booking(self.db, booking_id)
    
    def get_payments_for_bookings(self, booking_ids: list[UUID]):
        return self.repo.list_payments_for_bookings(self.db, booking_ids)

    def create_checkout_session(
        self,
        booking_id: UUID,
        user_id: str,
        amount: Decimal,
        currency: str,
        success_url: str,
        cancel_url: str,
        customer_email: str = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session for hosted payment page.
        """
        result = self.port.create_checkout_session(
            booking_id=str(booking_id),
            user_id=user_id,
            amount=amount,
            currency=currency,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
        )
        
        return result

    def verify_checkout_session(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """Verify a Stripe Checkout Session and get payment details."""
        return self.port.retrieve_checkout_session(session_id=session_id)

    def create_payment_intent(
        self,
        booking_id: UUID,
        amount: Decimal,
        currency: str = "USD",
    ) -> dict:
        """
        Create a Stripe PaymentIntent for frontend Stripe Elements.
        Returns client_secret for frontend payment confirmation.
        """
        # Use the port abstraction
        result = self.port.create_payment_intent(
            amount=amount,
            currency=currency,
            reference=str(booking_id),
            capture_method="manual",
        )
        
        # Store the PaymentIntent reference in our database
        payment = Payment(
            booking_id=booking_id,
            type=PaymentType.ESCROW,
            amount=amount,
            currency=currency,
            processor_ref=result["payment_intent_id"],
            status=PaymentStatus.AUTHORIZED,
        )
        self.repo.create_payment(self.db, payment)
        
        return {
            "client_secret": result["client_secret"],
            "payment_intent_id": result["payment_intent_id"],
            "amount": amount,
            "currency": currency
        }

def get_payments_service(
    db: Session = Depends(get_db),
    port: PaymentPort = Depends(get_payment_adapter),
    providers_public: ProvidersPublic = Depends(get_providers_public),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> PaymentsService:

    repo = PaymentsRepository()

    return PaymentsService(
        db=db,
        repo=repo,
        port=port,
        providers_public=providers_public,
        notifications_public=notifications_public,
    )