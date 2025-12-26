from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from .service import MetricsService, get_metrics_service
from .schemas import (
    MetricSampleCreate,
    MetricsQueryParams,
    MetricSampleRead,
    MetricSampleListItem,
)

from app.auth.auth import get_current_user


router = APIRouter()

# Provider (authenticated) ingestion endpoint
@router.post(
    "/machines/{machine_id}/ingest",
    response_model=MetricSampleRead,
    summary="Submit a metric sample for a machine",
)
def ingest_metric_sample(
    machine_id: UUID,
    payload: MetricSampleCreate,
    service: MetricsService = Depends(get_metrics_service),
    user=Depends(get_current_user),
):
    """
    Metrics ingestion endpoint.
    For now, authenticated providers can push metrics (mock agent flow).
    """
    try:
        return service.ingest_metrics(
            machine_id=machine_id,
            payload=payload,
            provider_id=user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@router.get(
    "/machines/{machine_id}",
    response_model=list[MetricSampleListItem],
    summary="List metrics for a machine",
)
def list_metrics_for_machine(
    machine_id: UUID,
    query: MetricsQueryParams = Depends(),
    user=Depends(get_current_user),
    service: MetricsService = Depends(get_metrics_service),
):
    """Any authenticated user may read machine metrics."""
    try:
        return service.list_machine_metrics(machine_id, query)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@router.get(
    "/machines/{machine_id}/latest",
    response_model=MetricSampleRead | None,
    summary="Get latest metric sample for a machine",
)
def get_latest_metrics(
    machine_id: UUID,
    user=Depends(get_current_user),
    service: MetricsService = Depends(get_metrics_service),
):
    """Returns newest sample, or null if there are none."""
    try:
        return service.get_latest_metrics(machine_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )