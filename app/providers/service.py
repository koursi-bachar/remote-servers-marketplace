from typing import Optional
from sqlalchemy.orm import Session

from .repository import ProviderRepository
from . import models, schemas

from fastapi import Depends

from app.database import get_db

class ProviderProfileService:
    def __init__(
        self,
        db: Session,
        repo: ProviderRepository,
    ):
        self.db = db
        self.repo = repo

    def create_profile(self, user_id, data: schemas.ProviderProfileCreate):
        if self.repo.get_by_user_id(user_id):
            raise ValueError("User already has a provider profile.")
        return self.repo.create(user_id, data)

    def update_profile(self, user_id, profile_id, data: schemas.ProviderProfileUpdate):
        profile = self.repo.get(profile_id)
        if not profile:
            raise ValueError("Provider profile not found.")
        if profile.user_id != user_id:
            raise ValueError("Forbidden.")
        return self.repo.update(profile, data)

    def require_profile(self, user_id):
        profile = self.repo.get_by_user_id(user_id)
        if not profile:
            raise ValueError("User is not a provider.")
        return profile

    def require_verified(self, user_id):
        profile = self.require_profile(user_id)
        if profile.verification_status != models.ProviderVerificationStatus.VERIFIED:
            raise ValueError("Provider not verified.")
        return profile

class VerificationService:
    def __init__(
        self,
        db: Session,
        repo: ProviderRepository,
    ):
        self.db = db
        self.repo = repo

    def create_verification_request(
        self,
        user_id,
        data: schemas.VerificationCreate,
    ):
        if data.subject_type == models.VerificationSubject.PROVIDER:
            profile = self.repo.get_by_user_id(user_id)
            if not profile:
                raise ValueError("User has no provider profile.")
            if profile.id != data.subject_id:
                raise ValueError("Forbidden.")
        return self.repo.create_verification(data)

    def admin_update_verification(
        self,
        admin_user_id,
        verification_id,
        new_status: schemas.VerificationStatus,
        notes: Optional[str] = None,
    ):
        """Admin can choose to approve or deny verification request."""
        verification = self.repo.get_verification(verification_id)
        if not verification:
            raise ValueError("Verification not found.")

        verification.status = new_status
        verification.notes = notes
        verification.performed_by_admin_id = admin_user_id

        if verification.subject_type == models.VerificationSubject.PROVIDER:
            profile = self.repo.get(verification.subject_id)
            if not profile:
                raise ValueError("Provider profile not found.")
            profile.verification_status = new_status

        return self.repo.save_verification(verification)

    def list_verifications(self, subject_type, subject_id):
        return self.repo.list_verifications_for(subject_type, subject_id)

def get_provider_profile_service(
    db: Session = Depends(get_db),
) -> ProviderProfileService:
    repo = ProviderRepository(db)
    return ProviderProfileService(
        db=db,
        repo=repo,
    )

def get_verification_service(
    db: Session = Depends(get_db),
) -> VerificationService:
    repo = ProviderRepository(db)
    return VerificationService(
        db=db,
        repo=repo,
    )