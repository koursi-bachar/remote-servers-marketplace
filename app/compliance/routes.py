from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from .schemas import (
    WipeAttestationCreate,
    WipeAttestationRead,
    WipeAttestationUpdateStatus,
    WipeAttestationPublic,
    WipeVerificationPublic
)
from .service import ComplianceService, get_compliance_service
from app.auth.public import ensure_provider, ensure_admin, get_auth_public, AuthPublic
from app.auth.auth import get_current_user


router = APIRouter()

#Provider submission
@router.post(
    "/attestations",
    response_model=WipeAttestationRead,
)
def submit_attestation(
    data: WipeAttestationCreate,
    current_user = Depends(ensure_provider),
    service: ComplianceService = Depends(get_compliance_service),
):
    provider_id = current_user.id
    return service.submit_attestation(provider_id, data)

#Admin review
@router.patch(
    "/attestations/{attestation_id}/review",
    response_model=WipeAttestationRead,
    dependencies=[Depends(ensure_admin)],
)
def review_attestation(
    attestation_id: UUID,
    data: WipeAttestationUpdateStatus,
    service: ComplianceService = Depends(get_compliance_service),
):
    return service.admin_review(attestation_id, data)

#Audit browsing (Admin)
@router.get(
    "/attestations",
    response_model=list[WipeAttestationRead],
    dependencies=[Depends(ensure_admin)],
)
def list_all(
    service: ComplianceService = Depends(get_compliance_service),
):
    return service.list_all_attestations()

# Machine wipe log (Provider/Admin)
@router.get(
    "/machines/{machine_id}/attestations",
    response_model=list[WipeAttestationRead],
)
def machine_attestations(
    machine_id: UUID,
    service: ComplianceService = Depends(get_compliance_service),
):
    return service.list_machine_attestations(machine_id)

# New wipe and attestation endpoints
@router.get("/buyer/booking/{booking_id}/wipe-verification", response_model=WipeVerificationPublic)
def get_wipe_verification(
    booking_id: UUID,
    user = Depends(get_current_user),
    auth: AuthPublic = Depends(get_auth_public),
    service: ComplianceService = Depends(get_compliance_service),
):
    """Buyer gets wipe verification status for their completed booking"""
    auth.ensure_buyer()
    
    # Service handles ownership check internally
    return service.get_buyer_verification(booking_id, user.id)

@router.get("/provider/booking/{booking_id}/wipe-attestation", response_model=WipeAttestationPublic)
def get_provider_attestation(
    booking_id: UUID,
    user = Depends(get_current_user),
    auth: AuthPublic = Depends(get_auth_public),
    service: ComplianceService = Depends(get_compliance_service),
):
    """Provider gets full wipe attestation for their machine"""
    auth.ensure_provider()
    return service.get_provider_attestation(user.id, booking_id)

@router.get("/admin/booking/{booking_id}/wipe-attestation", response_model=WipeAttestationPublic)
def get_admin_attestation(
    booking_id: UUID,
    user = Depends(get_current_user),
    auth: AuthPublic = Depends(get_auth_public),
    service: ComplianceService = Depends(get_compliance_service),
):
    """Admin gets full wipe attestation"""
    auth.ensure_admin()
    return service.get_admin_attestation(booking_id)