"""
Public interface for the Bookings domain module.
"""

from .service import BookingsService, get_bookings_service
from .repository import BookingsRepository
from .schemas import (
    BookingRead,
    BookingRequest,
    BookingAdminCreate,
    BookingStatus,
)
from .models import Booking

__all__ = [
    # Service
    "BookingsService",
    "get_bookings_service",

    # Repository
    "BookingsRepository",

    # Schemas
    "BookingRequest",
    "BookingAdminCreate",
    "BookingRead",
    "BookingStatus",

    # Models
    "Booking",
]