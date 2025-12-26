from typing import Protocol
from uuid import UUID

from fastapi import Depends

from .service import BookingsService, get_bookings_service


class BookingsPublic(Protocol):
    """Protocol defining the public interface for bookings queries."""
    def get_booking(self, booking_id: UUID):
        ...

    def is_active(self, booking) -> bool:
        ...

    def is_confirmed(self, booking) -> bool:
        ...

    def is_requested(self, booking) -> bool:
        ...

    def is_cancelled(self, booking) -> bool:
        ...

    def is_completed(self, booking) -> bool:
        ...

    def is_cancellable(self, booking) -> bool:
        ...

    def get_org_bookings_in_period(self, org_id, period_start, period_end):
        ...

class BookingsPublicImpl:
    """Concrete implementation of BookingsPublic using the BookingsService."""
    def __init__(self, service: BookingsService):
        self.service = service

    def get_booking(self, booking_id: UUID):
        return self.service.get_booking_readonly(booking_id)

    def is_active(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.ACTIVE

    def is_confirmed(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.CONFIRMED

    def is_requested(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.REQUESTED
    
    def is_cancelled(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.CANCELLED
    
    def is_completed(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.COMPLETED

    def is_cancellable(self, booking) -> bool:
        """Returns True if booking is in a cancellable state (REQUESTED or CONFIRMED)."""
        return booking.status in {
            self.service.BookingStatus.REQUESTED,
            self.service.BookingStatus.CONFIRMED,
        }

    def get_org_bookings_in_period(self, org_id, period_start, period_end):
        return self.service.get_org_bookings_in_period(org_id, period_start, period_end)

def get_bookings_public(
    service: BookingsService = Depends(get_bookings_service),
) -> BookingsPublic:
    """Dependency injection provider for BookingsPublic interface."""
    return BookingsPublicImpl(service)