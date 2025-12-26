from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID

from .repository import MachinesRepository
from .schemas import MachineCreate
from .models import Machine

from app.database import get_db
from app.providers.public import ProvidersPublic, get_providers_public


class MachinesService:
    """
    Service layer for machine CRUD and domain rules
    (authorization stays in routes).
    """
    def __init__(self, db: Session, machine_repo: MachinesRepository,
                 providers_public: ProvidersPublic):
        self.db = db
        self.machine_repo = machine_repo
        self.providers_public = providers_public

    def get_machine(self, machine_id: UUID) -> Machine:
        machine = self.machine_repo.get_machine(self.db, machine_id)
        if not machine:
            raise ValueError("Machine does not exist.")
        return machine

    def list_machines_for_provider(self, provider_id: UUID) -> list[Machine]:
        return self.machine_repo.list_machines_for_provider(self.db, provider_id)

    def create_machine(self, payload: MachineCreate) -> Machine:
        return self.machine_repo.create_machine(self.db, payload)

    def delete_machine(self, machine_id: UUID, provider_id: UUID):
        machine = self.machine_repo.get_machine(self.db, machine_id)
        if not machine:
            raise ValueError("Machine does not exist.")

        if machine.provider_id != provider_id:
            raise ValueError("You do not own this machine.")

        self.machine_repo.delete_machine(self.db, machine)

def get_machines_service(
    db: Session = Depends(get_db),
    providers_public: ProvidersPublic = Depends(get_providers_public),
) -> MachinesService:
    repo = MachinesRepository()
    return MachinesService(
        db=db,
        machine_repo=repo,
        providers_public=providers_public
    )