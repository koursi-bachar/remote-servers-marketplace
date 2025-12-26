from typing import Protocol
from uuid import UUID

from fastapi import Depends

from .service import MachinesService, get_machines_service


class MachinesPublic(Protocol):
    """Protocol defining the public interface for machines queries."""
    def provider_owns_machine(self, provider_id: UUID, machine_id: UUID) -> bool:
        ...

    def get_machine(self, machine_id: UUID):
        ...

    def list_machines_for_provider(self, provider_id: UUID):
        ...

class MachinesPublicImpl:
    """Concrete implementation of MachinesPublic using the MachinesService."""
    def __init__(self, service: MachinesService):
        self.service = service

    def provider_owns_machine(self, provider_id: UUID, machine_id: UUID) -> bool:
        try:
            machine = self.service.get_machine(machine_id)
        except ValueError:
            return False
        return machine.provider_id == provider_id

    def get_machine(self, machine_id: UUID):
        return self.service.get_machine(machine_id)

    def list_machines_for_provider(self, provider_id: UUID):
        return self.service.list_machines_for_provider(provider_id)

def get_machines_public(
    service: MachinesService = Depends(get_machines_service),
) -> MachinesPublic:
    """Dependency injection provider for MachinesService interface."""
    return MachinesPublicImpl(service)