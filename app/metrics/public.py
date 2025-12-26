from typing import Protocol, Optional
from uuid import UUID

from fastapi import Depends

from .service import MetricsService, get_metrics_service
from .schemas import MetricSampleListItem, MetricSampleRead, MetricsQueryParams


class MetricsPublic(Protocol):
    """Protocol defining the public interface for machines queries."""
    def get_latest_metrics(self, machine_id: UUID) -> Optional[MetricSampleRead]:
        ...

    def list_metrics_for_machine(
        self,
        machine_id: UUID,
        query: MetricsQueryParams,
    ) -> list[MetricSampleListItem]:
        ...

    def ingest_raw_metrics(self, machine_id: UUID, raw: dict, provider_id: UUID):
        ...


class MetricsPublicImpl:
    """Concrete implementation of MetricsPublic using the MetricsService."""
    def __init__(self, service: MetricsService):
        self.service = service

    def get_latest_metrics(self, machine_id: UUID) -> Optional[MetricSampleRead]:
        return self.service.get_latest_metrics(machine_id)

    def list_metrics_for_machine(
        self,
        machine_id: UUID,
        query: MetricsQueryParams,
    ) -> list[MetricSampleListItem]:
        return self.service.list_machine_metrics(machine_id, query)
    
    def ingest_raw_metrics(self, machine_id: UUID, raw: dict, provider_id: UUID):
        return self.service.ingest_raw_metrics(machine_id, raw, provider_id)

def get_metrics_public(
    service: MetricsService = Depends(get_metrics_service),
) -> MetricsPublic:
    """Dependency injection provider for MetricsService interface."""
    return MetricsPublicImpl(service)