from typing import List, Optional
from sqlalchemy.orm import Session

from .models import ProviderProfile, Verification, VerificationStatus
from .schemas import ProviderProfileUpdate, VerificationCreate, ProviderProfileCreate


class ProviderRepository:
    """
    Persistence layer for ProviderProfile + Verification.
    """
    def __init__(self, db: Session):
        self.db = db

    # ProviderProfile CRUD
    def get(self, profile_id) -> Optional[ProviderProfile]:
        return (
            self.db.query(ProviderProfile)
            .filter(ProviderProfile.id == profile_id)
            .first()
        )

    def get_by_user_id(self, user_id) -> Optional[ProviderProfile]:
        return (
            self.db.query(ProviderProfile)
            .filter(ProviderProfile.user_id == user_id)
            .first()
        )

    def create(
        self,
        user_id,
        data: ProviderProfileCreate,
    ) -> ProviderProfile:
        profile = ProviderProfile(
            user_id=user_id,
            payout_account_ref=data.payout_account_ref,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(
        self,
        profile: ProviderProfile,
        data: ProviderProfileUpdate,
    ) -> ProviderProfile:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        self.db.commit()
        self.db.refresh(profile)
        return profile

    # Verification CRUD
    def get_verification(
        self,
        verification_id,
    ) -> Optional[Verification]:
        return (
            self.db.query(Verification)
            .filter(Verification.id == verification_id)
            .first()
        )

    def create_verification(
        self,
        data: VerificationCreate,
    ) -> Verification:
        verification = Verification(
            subject_type=data.subject_type,
            subject_id=data.subject_id,
            notes=data.notes,
        )
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        return verification

    def update_verification(
        self,
        verification: Verification,
        new_status: VerificationStatus,
        notes: str | None,
        admin_user_id,
    ) -> Verification:
        verification.status = new_status
        verification.notes = notes
        verification.performed_by_admin_id = admin_user_id

        self.db.commit()
        self.db.refresh(verification)
        return verification

    def list_verifications_for(
        self, subject_type, subject_id
    ) -> List[Verification]:
        return (
            self.db.query(Verification)
            .filter(
                Verification.subject_type == subject_type,
                Verification.subject_id == subject_id,
            )
            .order_by(Verification.created_at.desc())
            .all()
        )
    
    def save_verification(
        self,
        verification: Verification,
    ) -> Verification:
        self.db.commit()
        self.db.refresh(verification)
        return verification