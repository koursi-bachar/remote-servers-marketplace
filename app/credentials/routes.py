from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.auth.auth import get_current_user
from app.auth.public import get_auth_public, AuthPublic

from .service import AccessCredentialsService, get_access_credential_service
from app.bookings.public import BookingsPublic, get_bookings_public


router = APIRouter()

@router.get("/buyer/{booking_id}")
def get_buyer_credentials(
    booking_id: UUID,
    user = Depends(get_current_user),
    auth: AuthPublic = Depends(get_auth_public),
    service: AccessCredentialsService = Depends(get_access_credential_service),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
):
    auth.ensure_buyer()

    booking = bookings_public.get_booking(booking_id)

    if booking.buyer_user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this booking.",
        )

    creds = service.get_for_booking(booking)
    return {"credentials": creds}

@router.get("/provider/{booking_id}")
def get_provider_credentials(
    booking_id: UUID,
    user = Depends(get_current_user),
    auth: AuthPublic = Depends(get_auth_public),
    service: AccessCredentialsService = Depends(get_access_credential_service),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
):
    auth.ensure_provider()

    booking = bookings_public.get_booking(booking_id)

    #Provider owns the machine
    machine_owner_id = booking.listing.machine.provider_id
    if user.id != machine_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the provider of this machine.",
        )

    creds = service.get_for_booking(booking)
    return {"credentials": creds}