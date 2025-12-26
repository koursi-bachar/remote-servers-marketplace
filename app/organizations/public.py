from fastapi import Depends
from typing import Protocol, List
from uuid import UUID

from .service import OrganizationsService, get_organization_service
from .models import Organization, OrganizationMembership


class OrganizationsPublic(Protocol):
    """Protocol defining the public interface for organizations queries."""
    def get_organization(self, org_id: UUID) -> Organization | None:
        ...

    def is_org_admin(self, user_id: UUID, org_id: UUID) -> bool:
        ...

    def is_org_member(self, user_id: UUID, org_id: UUID) -> bool:
        ...

    def list_user_organizations(self, user_id: UUID) -> List[Organization]:
        ...

    def get_membership(
        self, org_id: UUID, user_id: UUID
    ) -> OrganizationMembership | None:
        ...

class OrganizationsPublicImpl(OrganizationsPublic):
    """Concrete implementation of OrganizationsPublic using the OrganizationsService."""
    def __init__(self, service: OrganizationsService):
        self.service = service

    # Orgs
    def get_organization(self, org_id: UUID):
        return self.service.repo.get(org_id)

    # Permission helpers
    def is_org_admin(self, user_id: UUID, org_id: UUID) -> bool:
        return self.service.is_org_admin(user_id, org_id)

    def is_org_member(self, user_id: UUID, org_id: UUID) -> bool:
        return self.service.is_org_member(user_id, org_id)

    # User's org list
    def list_user_organizations(self, user_id: UUID):
        return self.service.list_user_organizations(user_id)

    # Membership lookup
    def get_membership(self, org_id: UUID, user_id: UUID):
        return self.service.repo.get_membership(org_id, user_id)


def get_organizations_public(
    service: OrganizationsService = Depends(get_organization_service),
) -> OrganizationsPublic:
    """Dependency injection provider for OrganizationsService interface."""
    return OrganizationsPublicImpl(service)