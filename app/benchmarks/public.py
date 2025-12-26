from typing import List, Optional
from uuid import UUID
from typing_extensions import Protocol
from fastapi import Depends
from .service import BenchmarkService, get_benchmark_service
from .schemas import BenchmarkRead, BenchmarkCreate


class BenchmarksPublic(Protocol):
    """Protocol defining the public interface for benchmarks queries."""
    def get_benchmarks_for_machine(self, machine_id: UUID) -> List[BenchmarkRead]:
        ...
    
    def get_benchmarks_for_listing(self, listing_id: UUID) -> List[BenchmarkRead]:
        ...

class BenchmarksPublicImpl(BenchmarksPublic):
    """Concrete implementation of BenchmarksPublic using the BenchmarksService."""
    def __init__(self, service: BenchmarkService):
        self.service = service

    def get_benchmarks_for_machine(self, machine_id: UUID):
        return self.service.list_machine_benchmarks(machine_id)

    def get_benchmarks_for_listing(self, listing_id: UUID):
        return self.service.list_listing_benchmarks(listing_id)

def get_benchmarks_public(
    service: BenchmarkService = Depends(get_benchmark_service),
):
    """Dependency injection provider for BenchmarksPublic interface."""
    return BenchmarksPublicImpl(service)