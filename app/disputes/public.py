from typing import Protocol, List
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.disputes.service import DisputesService, get_disputes_service
from app.disputes.models import Dispute, DisputeStatus
from app.disputes.schemas import (
    DisputeCreate,
    DisputeResolution,
)


class DisputesPublic(Protocol):
    """Protocol defining the public interface for disputes queries."""
    def open_dispute(self, user_id: UUID, payload: DisputeCreate) -> Dispute:
        ...

    def list_disputes_for_user(self, user_id: UUID) -> List[Dispute]:
        ...

    def list_disputes_for_booking(self, booking_id: UUID) -> List[Dispute]:
        ...

    def list_open_for_admin(self) -> List[Dispute]:
        ...

    def set_status(
        self,
        dispute_id: UUID,
        *,
        new_status: DisputeStatus,
        resolution_notes: str | None = None,
    ) -> Dispute:
        ...

    def resolve_dispute(
        self,
        dispute_id: UUID,
        payload: DisputeResolution,
    ) -> Dispute:
        ...

    def close_dispute(self, dispute_id: UUID) -> Dispute:
        ...

    def list_all_for_admin(self) -> List[Dispute]:
        ...


class DisputesPublicImpl(DisputesPublic):
    """Concrete implementation of DisputesPublic using the DisputesService."""
    def __init__(self, service: DisputesService):
        self.service = service

    def open_dispute(self, user_id: UUID, payload: DisputeCreate) -> Dispute:
        return self.service.open_dispute(user_id, payload)

    def list_disputes_for_user(self, user_id: UUID):
        return self.service.list_disputes_for_user(user_id)

    def list_disputes_for_booking(self, booking_id: UUID):
        return self.service.list_disputes_for_booking(booking_id)

    def list_open_for_admin(self) -> List[Dispute]:  
        return self.service.list_open_for_admin()

    def set_status(
        self,
        dispute_id: UUID,
        *,
        new_status: DisputeStatus,
        resolution_notes: str | None = None,
    ):
        return self.service.set_status(
            dispute_id,
            new_status=new_status,
            resolution_notes=resolution_notes,
        )

    def resolve_dispute(self, dispute_id: UUID, payload: DisputeResolution):
        return self.service.resolve_dispute(dispute_id, payload)

    def close_dispute(self, dispute_id: UUID):
        return self.service.close_dispute(dispute_id)
    
    def list_all_for_admin(self) -> List[Dispute]:
        return self.service.list_all_for_admin()

def get_disputes_public(
    service: DisputesService = Depends(get_disputes_service),
) -> DisputesPublic:
    """Dependency injection provider for DisputesService interface."""
    return DisputesPublicImpl(service)