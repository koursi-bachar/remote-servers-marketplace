from typing import Protocol
from uuid import UUID
from fastapi import Depends
from app.database import get_db
from sqlalchemy.orm import Session

from .service import AccessCredentialsService, get_access_credential_service


class AccessCredentialsPublic(Protocol):
    """Protocol defining the public interface for credentials queries."""
    def issue_for_booking(self, booking):
        ...

    def revoke_for_booking(self, booking):
        ...

    def get_for_booking(self, booking):
        ...

class AccessCredentialsPublicImpl:
    """Concrete implementation of AccessCredentialsPublic using the AccessCredentialsService."""
    def __init__(self, svc: AccessCredentialsService):
        self.svc = svc

    def issue_for_booking(self, booking):
        return self.svc.issue_for_booking(booking)

    def revoke_for_booking(self, booking):
        return self.svc.revoke_for_booking(booking)

    def get_for_booking(self, booking):
        return self.svc.get_for_booking(booking)


def get_credentials_public(
    svc: AccessCredentialsService = Depends(get_access_credential_service)
) -> AccessCredentialsPublic:
    """Dependency injection provider for AccessCredentialsService interface."""
    return AccessCredentialsPublicImpl(svc)