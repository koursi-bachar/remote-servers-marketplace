"""
Authorization rules for booking operations.

Defines which user roles can perform specific booking actions (confirm, cancel,
start/end sessions) based on ownership and relationship validation.
"""

from app.users.models import UserRole


def booking_has_valid_relationships(booking):
    """
    Validates that a booking has all required linked entities populated.
    
    Ensures booking → listing → machine → provider chain exists before
    checking permissions that depend on provider ownership.
    """
    if booking.listing is None:
        return False
    if booking.listing.machine is None:
        return False
    if booking.listing.machine.provider_id is None:
        return False
    return True

def can_confirm_booking(user, booking):
    """
    Determines if a user can confirm a booking.
    
    Rules:
    - ADMIN: always allowed
    - PROVIDER: only if they own the machine associated with the booking
    - BUYER: never allowed (buyers don't confirm bookings)
    """
    if not booking_has_valid_relationships(booking):
        return False

    if user.role == UserRole.ADMIN:
        return True

    provider_id = booking.listing.machine.provider_id

    if user.role == UserRole.PROVIDER and user.id == provider_id:
        return True

    return False

def can_cancel_booking(user, booking):
    """
    Determines if a user can cancel a booking.
    
    Rules:
    - ADMIN: always allowed
    - PROVIDER: if they own the machine (before session starts)
    - BUYER: only their own bookings (before session starts)
    """
    if not booking_has_valid_relationships(booking):
        return False

    # Buyer can cancel their own bookings before start
    if user.role == UserRole.BUYER and user.id == booking.buyer_user_id:
        return True

    # Provider can cancel bookings for machines they own before start
    provider_id = booking.listing.machine.provider_id
    if user.role == UserRole.PROVIDER and user.id == provider_id:
        return True

    # Admin can cancel always
    if user.role == UserRole.ADMIN:
        return True

    return False

def can_start_session(user, booking):
    """
    Determines if a user can start a booking session.
    
    Rules:
    - ADMIN: always allowed
    - PROVIDER: only if they own the machine
    - BUYER: never allowed (only providers start sessions)
    """
    if not booking_has_valid_relationships(booking):
        return False

    if user.role == UserRole.ADMIN:
        return True

    provider_id = booking.listing.machine.provider_id
    if user.role == UserRole.PROVIDER and user.id == provider_id:
        return True

    # Buyers never allowed
    return False

def can_end_session(user, booking):
    """
    Determines if a user can end a booking session.
    
    Rules:
    - ADMIN: always allowed
    - PROVIDER: only if they own the machine
    - BUYER: never allowed (only providers end sessions)
    """
    if not booking_has_valid_relationships(booking):
        return False

    if user.role == UserRole.ADMIN:
        return True

    provider_id = booking.listing.machine.provider_id
    if user.role == UserRole.PROVIDER and user.id == provider_id:
        return True

    return False