from typing import Protocol, List
from decimal import Decimal

from fastapi import Depends

from .service import PaymentsService, get_payments_service
from .models import Payment


class PaymentsPublic(Protocol):
    """Protocol defining the public interface for payments queries."""
    def escrow_for_booking(
        self,
        booking,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        ...

    def capture_for_booking(
        self,
        booking,
    ) -> Payment:
        ...

    def refund_for_booking(
        self,
        booking_id,
        reason: str | None = None,
    ) -> Payment:
        ...

    def list_for_booking(
        self,
        booking,
    ) -> List[Payment]:
        ...

    def void_escrow_for_booking(
        self,
        booking,
    ) -> Payment:
        ...

    def get_payments_for_bookings(self, booking_ids):
        ...


class PaymentsPublicImpl(PaymentsPublic):
    """Concrete implementation of PaymentsPublic using the PaymentsService."""
    def __init__(self, service: PaymentsService):
        self.service = service

    def escrow_for_booking(
        self,
        booking,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        return self.service.create_escrow(
            booking=booking,
            amount=amount,
            currency=currency,
        )

    def capture_for_booking(
        self,
        booking,
    ) -> Payment:
        return self.service.capture(
            booking=booking,
        )

    def refund_for_booking(
        self,
        booking_id,
        reason: str | None = None,
    ) -> Payment:
        return self.service.refund(
            booking_id=booking_id,
            reason=reason,
        )

    def list_for_booking(
        self,
        booking_id,
    ):
        return self.service.list_for_booking(booking_id)
    
    def void_escrow_for_booking(
        self,
        booking,
    ) -> Payment:
        return self.service.void_escrow(booking=booking)
    
    def get_payments_for_bookings(self, booking_ids):
        return self.service.get_payments_for_bookings(booking_ids)


def get_payments_public(
    service: PaymentsService = Depends(get_payments_service),
) -> PaymentsPublic:
    """Dependency injection provider for PaymentsService interface."""
    return PaymentsPublicImpl(service)