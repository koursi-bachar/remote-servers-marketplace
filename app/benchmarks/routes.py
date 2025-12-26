from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import Optional
from app.auth.auth import get_current_user
from .service import BenchmarkService, get_benchmark_service
from .schemas import BenchmarkCreate, BenchmarkRead
from app.users.models import User, UserRole


router = APIRouter()

#Provider upload
@router.post("/machines/{machine_id}", response_model=BenchmarkRead, status_code=201)
def create_machine_benchmark(
    machine_id: UUID,
    benchmark: BenchmarkCreate,
    user: User = Depends(get_current_user),
    service: BenchmarkService = Depends(get_benchmark_service),
):
    if user.role != UserRole.PROVIDER:
        raise HTTPException(403, "Only providers can upload benchmarks")
    
    return service.create_benchmark(
        machine_id=machine_id,
        provider_id=user.id,
        name=benchmark.name,
        score=benchmark.score,
        methodology_uri=benchmark.methodology_uri,
        artifact_uri=benchmark.artifact_uri
    )
    
@router.get("/machines/{machine_id}", response_model=list[BenchmarkRead])
def get_machine_benchmarks(
    machine_id: UUID,
    service: BenchmarkService = Depends(get_benchmark_service),
):
    return service.list_machine_benchmarks(machine_id)

@router.get("/listings/{listing_id}", response_model=list[BenchmarkRead])
def get_listing_benchmarks(
    listing_id: UUID,
    service: BenchmarkService = Depends(get_benchmark_service),
):
    return service.list_listing_benchmarks(listing_id)