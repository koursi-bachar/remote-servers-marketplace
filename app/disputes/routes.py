from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.auth.auth import get_current_user
from app.users.models import User, UserRole

from app.disputes.public import DisputesPublic, get_disputes_public
from app.disputes.schemas import (
    DisputeCreate,
    DisputeRead,
    DisputeListItem,
    DisputeResolution,
)
from app.disputes.models import DisputeStatus


router = APIRouter()

@router.post("/", response_model=DisputeRead, status_code=201)
def open_dispute(
    payload: DisputeCreate,
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    """
    Buyers or providers open a dispute on a booking they are involved with.
    """
    try:
        return disputes.open_dispute(user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=list[DisputeListItem])
def list_my_disputes(
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    return disputes.list_disputes_for_user(user.id)

@router.get("/booking/{booking_id:uuid}", response_model=list[DisputeListItem])
def list_disputes_for_booking(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    """
    Providers or buyers may want to inspect disputes for a specific booking.
    """
    try:
        return disputes.list_disputes_for_booking(booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/admin", response_model=list[DisputeListItem])
def list_open_disputes_for_admin(
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admins only")

    return disputes.list_open_for_admin()

@router.put("/{dispute_id:uuid}/status", response_model=DisputeRead)
def update_dispute_status(
    dispute_id: UUID,
    new_status: DisputeStatus,
    resolution_notes: str | None = None,
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admins only")

    try:
        return disputes.set_status(
            dispute_id,
            new_status=new_status,
            resolution_notes=resolution_notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dispute_id:uuid}/resolve", response_model=DisputeRead)
def resolve_dispute(
    dispute_id: UUID,
    payload: DisputeResolution,
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admins only")

    try:
        return disputes.resolve_dispute(dispute_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dispute_id:uuid}/close", response_model=DisputeRead)
def close_dispute(
    dispute_id: UUID,
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admins only")

    try:
        return disputes.close_dispute(dispute_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/admin/all", response_model=list[DisputeListItem])
def list_all_disputes_for_admin(
    user: User = Depends(get_current_user),
    disputes: DisputesPublic = Depends(get_disputes_public),
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admins only")
    
    return disputes.list_all_for_admin()