from fastapi import Depends, APIRouter, HTTPException
from uuid import UUID

from app.auth.auth import get_current_user
from app.users.models import User, UserRole

from .schemas import MachineCreate, MachineRead
from .service import MachinesService, get_machines_service

router = APIRouter()


@router.get("/{machine_id:uuid}", response_model=MachineRead)
def get_machine(
    machine_id: UUID,
    user: User = Depends(get_current_user),
    service: MachinesService = Depends(get_machines_service),
):
    try:
        machine = service.get_machine(machine_id)
    except ValueError as e:
        raise HTTPException(404, "Machine not found")

    #Provider authorization
    if user.role == UserRole.PROVIDER and machine.provider_id != user.id:
        raise HTTPException(403, "Not allowed")

    return machine

@router.get("/", response_model=list[MachineRead])
def list_machines(
    user: User = Depends(get_current_user),
    service: MachinesService = Depends(get_machines_service),
):
    if user.role != UserRole.PROVIDER:
        raise HTTPException(403, "Only providers can view machines")

    return service.list_machines_for_provider(user.id)

@router.delete("/{machine_id:uuid}", status_code=204)
def delete_machine(
    machine_id: UUID,
    user: User = Depends(get_current_user),
    service: MachinesService = Depends(get_machines_service),
):
    try:
        service.delete_machine(machine_id, provider_id=user.id)
    except ValueError as e:
        raise HTTPException(404, "Machine not found")
    except ValueError as e:
        raise HTTPException(403, "Not allowed")

@router.post("/", response_model=MachineRead, status_code=201)
def create_machine(
    machine: MachineCreate,
    user: User = Depends(get_current_user),
    service: MachinesService = Depends(get_machines_service),
):
    if user.role != UserRole.PROVIDER:
        raise HTTPException(403, "Only providers can create machines")

    #Force provider ID
    machine.provider_id = user.id

    return service.create_machine(payload=machine)