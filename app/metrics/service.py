from fastapi import Depends
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from .repository import MetricsRepository
from .schemas import (
    MetricSampleCreate,
    MetricSampleRead,
    MetricSampleListItem,
    MetricsQueryParams,
)

from app.machines.public import MachinesPublic, get_machines_public
from app.database import get_db


class MetricsService:
    """
    Service layer for Metrics domain.
    Enforces domain rules:
    - Machine existence validation
    - Provider ownership validation (via MachinesPublic)
    - Append-only metric ingestion
    """
    def __init__(
        self,
        db: Session,
        repo: MetricsRepository,
        machines_public: MachinesPublic,
    ):
        self.db = db
        self.repo = repo
        self.machines_public = machines_public

    #Ingest (ProviderAgentClient)
    def ingest_metrics(
        self,
        machine_id: UUID,
        payload: MetricSampleCreate,
        provider_id: UUID,
    ) -> MetricSampleRead:
        """Only provider agents for the machine owner may submit metrics."""
        machine = self.machines_public.get_machine(machine_id)
        if not machine:
            raise ValueError("Machine does not exist.")

        if not self.machines_public.provider_owns_machine(
            provider_id=provider_id,
            machine_id=machine_id,
        ):
            raise PermissionError("User does not own machine.")

        recorded_at = payload.recorded_at or datetime.now(timezone.utc)

        sample = self.repo.create_sample(
            self.db,
            machine_id=machine_id,
            recorded_at=recorded_at,
            gpu_util=payload.gpu_util,
            cpu_util=payload.cpu_util,
            mem_used_gb=payload.mem_used_gb,
            net_rx_mb=payload.net_rx_mb,
            net_tx_mb=payload.net_tx_mb,
        )

        return MetricSampleRead.model_validate(sample)

    def ingest_raw_metrics(self, machine_id: UUID, raw: dict, provider_id: UUID):
        """
        Converts raw agent metrics into MetricSampleCreate and delegates to ingest_metrics.
        Keeps DTO construction inside the domain layer.
        """
        payload = MetricSampleCreate(
            recorded_at=raw.get("collected_at"),
            gpu_util=raw.get("gpu_util"),
            cpu_util=raw.get("cpu_util"),
            mem_used_gb=raw.get("mem_gb"),
        )

        return self.ingest_metrics(
            machine_id=machine_id,
            payload=payload,
            provider_id=provider_id,
        )

    def list_machine_metrics(
        self,
        machine_id: UUID,
        query: MetricsQueryParams,
    ) -> list[MetricSampleListItem]:
        machine = self.machines_public.get_machine(machine_id)
        if not machine:
            raise ValueError("Machine does not exist.")

        samples = self.repo.list_samples(
            self.db,
            machine_id=machine_id,
            start=query.start,
            end=query.end,
            limit=query.limit,
        )

        return [MetricSampleListItem.model_validate(s) for s in samples]

    def get_latest_metrics(
        self,
        machine_id: UUID,
    ) -> Optional[MetricSampleRead]:

        machine = self.machines_public.get_machine(machine_id)
        if not machine:
            raise ValueError("Machine does not exist.")

        sample = self.repo.get_latest_sample(self.db, machine_id)
        if not sample:
            return None

        return MetricSampleRead.model_validate(sample)

def get_metrics_service(
    db: Session = Depends(get_db),
    machines_public: MachinesPublic = Depends(get_machines_public),
) -> MetricsService:

    repo = MetricsRepository()
    return MetricsService(
        db=db,
        repo=repo,
        machines_public=machines_public,
    )