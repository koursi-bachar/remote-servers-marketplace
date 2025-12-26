from fastapi import Depends
from typing import Protocol
from uuid import UUID

from .service import (
    ProviderProfileService,
    VerificationService,
    get_provider_profile_service,
    get_verification_service,
)
from .models import ProviderVerificationStatus


class ProvidersPublic(Protocol):
    """Protocol defining the public interface for providers queries."""
    def get_profile_by_user(self, user_id: UUID):
        ...

    def require_verified_provider(self, user_id: UUID):
        ...

    def is_verified(self, user_id: UUID) -> bool:
        ...

    def list_verifications(self, subject_type, subject_id):
        ...

class ProvidersPublicImpl:
    """Concrete implementation of ProvidersPublic using the ProviderProfileService and VerificationService."""
    def __init__(
        self,
        profile_service: ProviderProfileService,
        verification_service: VerificationService,
    ):
        self.profile_service = profile_service
        self.verification_service = verification_service

    def get_profile_by_user(self, user_id):
        return self.profile_service.repo.get_by_user_id(user_id)

    def require_verified_provider(self, user_id):
        return self.profile_service.require_verified(user_id)

    def is_verified(self, user_id) -> bool:
        profile = self.get_profile_by_user(user_id)
        return (
            profile is not None
            and profile.verification_status == ProviderVerificationStatus.VERIFIED
        )

    def list_verifications(self, subject_type, subject_id):
        return self.verification_service.list_verifications(subject_type, subject_id)

def get_providers_public(
    profile_service: ProviderProfileService = Depends(get_provider_profile_service),
    verification_service: VerificationService = Depends(get_verification_service),
) -> ProvidersPublic:
    """Dependency injection provider for ProviderProfileService and VerificationService interface."""
    return ProvidersPublicImpl(
        profile_service=profile_service,
        verification_service=verification_service,
    )