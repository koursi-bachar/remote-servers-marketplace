from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth import get_current_user
from app.auth.public import ensure_admin

from .models import ProviderProfile, VerificationSubject
from .schemas import (
    ProviderProfileCreate,
    ProviderProfileUpdate,
    ProviderProfileRead,
    VerificationCreate,
    VerificationUpdateStatus,
    VerificationRead,
)
from .public import ProvidersPublic, get_providers_public
from app.users.public import UsersPublic, get_users_public

from app.users.models import User

from app.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()

#Provider profiles
@router.post("/me", response_model=ProviderProfileRead, status_code=201)
def create_my_provider_profile(
    payload: ProviderProfileCreate,
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    try:
        return providers.profile_service.create_profile(user.id, payload)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.patch("/me", response_model=ProviderProfileRead)
def update_my_provider_profile(
    payload: ProviderProfileUpdate,
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    profile = providers.get_profile_by_user(user.id)
    if not profile:
        raise HTTPException(404, "Provider profile not found.")
    try:
        return providers.profile_service.update_profile(user.id, profile.id, payload)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/me", response_model=ProviderProfileRead)
def get_my_provider_profile(
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    profile = providers.get_profile_by_user(user.id)
    if not profile:
        raise HTTPException(404, "Provider profile not found.")
    return profile

#Verification (user requests verification)
@router.post("/me/verification", response_model=VerificationRead, status_code=201)
def request_provider_verification(
    payload: VerificationCreate,
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    try:
        return providers.verification_service.create_verification_request(
            user.id, payload
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/me/verifications", response_model=list[VerificationRead])
def list_my_verifications(
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    profile = providers.get_profile_by_user(user.id)
    if not profile:
        raise HTTPException(404, "Provider profile not found.")
    return providers.list_verifications("provider", profile.id)

#Admin review of verification entries
@router.post("/verification/{verification_id}/review", response_model=VerificationRead)
def admin_review_verification(
    verification_id: str,
    payload: VerificationUpdateStatus,
    admin: User = Depends(ensure_admin),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    try:
        return providers.verification_service.admin_update_verification(
            admin.id,
            verification_id,
            payload.status,
            payload.notes,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

#Admin: list verification events
@router.get("/verification/{subject_type}/{subject_id}", response_model=list[VerificationRead])
def admin_list_verifications_for_subject(
    subject_type: str,
    subject_id: str,
    admin: User = Depends(ensure_admin),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    return providers.list_verifications(subject_type, subject_id)

@router.get("/admin/providers")
def get_all_providers(
    admin: User = Depends(ensure_admin),
    db: Session = Depends(get_db),
    users_public: UsersPublic = Depends(get_users_public),
):
    """Get all provider profiles with user information"""
    providers = db.query(ProviderProfile).all()
    
    result = []
    for provider in providers:
        user = users_public.get_user(provider.user_id)
        result.append({
            "id": provider.id,
            "user_id": provider.user_id,
            "user_email": user.email if user else "Unknown",
            "verification_status": provider.verification_status.value,
            "payout_account_ref": provider.payout_account_ref,
            "created_at": provider.created_at,
            "updated_at": provider.updated_at,
        })
    
    return result

@router.get("/admin/providers/{provider_id}/verifications")
def get_provider_verifications(
    provider_id: str,
    admin: User = Depends(ensure_admin),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    """Get all verifications for a specific provider"""
    return providers.list_verifications(VerificationSubject.PROVIDER, provider_id)

@router.get("/admin/stats")
def get_provider_stats(
    admin: User = Depends(ensure_admin),
    db: Session = Depends(get_db),
):
    """Get provider statistics for admin dashboard"""
    total = db.query(ProviderProfile).count()
    pending = db.query(ProviderProfile).filter(
        ProviderProfile.verification_status == "pending"
    ).count()
    verified = db.query(ProviderProfile).filter(
        ProviderProfile.verification_status == "verified"
    ).count()
    rejected = db.query(ProviderProfile).filter(
        ProviderProfile.verification_status == "rejected"
    ).count()
    
    return {
        "total_providers": total,
        "pending_verification": pending,
        "verified_providers": verified,
        "rejected_providers": rejected,
    }