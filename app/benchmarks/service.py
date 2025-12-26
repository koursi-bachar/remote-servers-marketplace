from typing import List, Optional
from app.database import get_db
from uuid import UUID
from sqlalchemy.orm import Session
from .repository import BenchmarksRepository
from .schemas import BenchmarkCreate, BenchmarkRead
from fastapi import Depends

from app.machines.public import MachinesPublic, get_machines_public


class BenchmarkService:
    """Business logic for benchmark operations, including ownership validation."""
    def __init__(
        self,
        db: Session,
        repo: BenchmarksRepository,
        machines_public: MachinesPublic,
    ):
        self.db = db
        self.repo = repo
        self.machines_public = machines_public

    def create_benchmark(
        self,
        machine_id: UUID,
        provider_id: UUID,
        name: str,
        score: str,
        methodology_uri: Optional[str] = None,
        artifact_uri: Optional[str] = None,
    ) -> BenchmarkRead:
        # Authorization: verify provider owns the machine before creating benchmark
        if not self.machines_public.provider_owns_machine(provider_id, machine_id):
            raise PermissionError("User does not own this machine")
        
        payload = BenchmarkCreate(
            name=name,
            score=score,
            methodology_uri=methodology_uri,
            artifact_uri=artifact_uri,
            listing_id=None
        )
        return self.repo.create(self.db, machine_id, payload)

    def list_machine_benchmarks(self, machine_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_machine(self.db, machine_id)

    def list_listing_benchmarks(self, listing_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_listing(self.db, listing_id)

def get_benchmark_service(
    db: Session = Depends(get_db),
    machines_public: MachinesPublic = Depends(get_machines_public),
):
    """Dependency injection factory for BenchmarksService."""
    repo = BenchmarksRepository()
    return BenchmarkService(
        db=db,
        repo=repo,
        machines_public=machines_public,
    )