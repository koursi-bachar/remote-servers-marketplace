"""
Routes for managing the booking lifecycle.
Buyers:
    - Can request a booking (`POST /request`)
    - Can see their own bookings
Providers:
    - Can view bookings on their own machines
Admins:
    - Can view all bookings
    - Can create bookings manually
All business logic lives in bookings_service.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from app.auth.auth import get_current_user
from .permissions import (
    can_confirm_booking,
    can_cancel_booking,
    can_start_session,
    can_end_session,
)

from .models import BookingStatus
from .schemas import (
    BookingRead,
    BookingRequest,
    BookingAdminCreate,
)
from .service import (
    BookingsService,
    get_bookings_service,
)
from app.users.models import User, UserRole
from app.payments.models import PaymentStatus

from app.payments.public import PaymentsPublic, get_payments_public
from app.organizations.public import get_organizations_public, OrganizationsPublic


router = APIRouter()

@router.post("/", response_model=BookingRead, status_code=201)
def create_booking(
    booking: BookingAdminCreate,
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    """
    Admins use this to create bookings manually 
    Regular buyers will use use the /request endpoint, 
    which pulls their user id automatically.
    """
    if user.role == UserRole.ADMIN:
        try:
            return service.admin_create_booking(payload=booking)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) 
    else:
        raise HTTPException(403)


@router.get("/", response_model=list[BookingRead])
def list_bookings(
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    #Buyer sees only their own bookings
    if user.role == UserRole.BUYER:
        return service.list_bookings_for_user(user.id)

    #Provider sees bookings only for their own machines
    if user.role == UserRole.PROVIDER:
        return service.list_bookings_for_provider(user.id)

    #Admins see everything
    if user.role == UserRole.ADMIN:
        return service.list_all_bookings()
    
    else:
        raise HTTPException(403)

@router.post("/request", response_model=BookingRead)
def request_booking(
    booking: BookingRequest,
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    """
    Buyers don't send their own ID in the request.
    Verify the authenticated user to decide the buyer identity.
    """
    try:
        return service.request_booking(user.id, payload=booking)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/request-with-payment", response_model=BookingRead)
def request_booking_with_payment(
    booking: BookingRequest,
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    """
    Create booking in "pending_payment" status and return booking ID.
    Frontend will then call payments/checkout with this booking ID.
    """
    try:
        booking_obj = service.create_booking_draft(user.id, payload=booking)
        
        return booking_obj
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{booking_id}/confirm-payment", response_model=BookingRead)
def confirm_booking_payment(
    booking_id: UUID,
    service: BookingsService = Depends(get_bookings_service),
    payments_public: PaymentsPublic = Depends(get_payments_public),
    user=Depends(get_current_user),
):
    """
    Check if payment exists and update booking from "pending_payment" to "requested".
    Called by frontend after payment success page loads.
    """
    try:
        booking = service.get_booking_readonly(booking_id)
        
        payments = payments_public.list_for_booking(booking_id)
        if not payments or payments[0].status != PaymentStatus.AUTHORIZED:
            raise ValueError("No authorized payment found for this booking")
        
        booking.status = BookingStatus.REQUESTED
        service.booking_repo.update_booking(service.db, booking)
        
        return booking
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{booking_id:uuid}/confirm", response_model=BookingRead)
def confirm_booking(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

    if can_confirm_booking(user, booking):
        return service.confirm_booking(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id:uuid}/cancel", response_model=BookingRead)
def cancel_booking(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_cancel_booking(user, booking):
        return service.cancel_booking(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id:uuid}/start", response_model=BookingRead)
def start_booking_session(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_start_session(user, booking):
        return service.start_session(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id:uuid}/end", response_model=BookingRead)
def end_booking_session(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_end_session(user, booking):
        return service.end_session(booking_id, booking=booking)
    else:
        raise HTTPException(403)
    

@router.get("/organization/{org_id:uuid}", response_model=List[BookingRead])
def get_organization_bookings(
    org_id: UUID,
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
    organizations_public: OrganizationsPublic = Depends(get_organizations_public),  # Use the public interface
):
    """
    Get all bookings for an organization that the user has access to.
    """
    # Check if user is member of organization
    if not organizations_public.is_org_member(user.id, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    # Get bookings for organization
    # You'll need to add this method to BookingsService
    return service.get_bookings_for_organization(org_id)