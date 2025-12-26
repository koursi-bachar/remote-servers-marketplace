"""
Endpoints for listing servers.
Providers and Admins can create listings.
Everyone (including anonymous users) can browse listings.
"""

from fastapi import Depends, APIRouter, HTTPException
from typing import Optional

from app.users.models import User, UserRole
from app.auth.auth import require_roles, get_current_user

from .schemas import ListingCreate, ListingRead, ListingFilter
from .service import ListingsService, get_listings_service


router = APIRouter()

@router.post(
    "/",
    response_model=ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(UserRole.PROVIDER, UserRole.ADMIN))],
)
def create_listing(
    listing: ListingCreate,
    user: User = Depends(get_current_user),
    service: ListingsService = Depends(get_listings_service),
):
    """
    Create a new listing.
    Providers use this to publish a server. We validate ownership and domain
    rules in the service layer. Any domain errors are translated here into
    proper HTTP responses.
    """
    try:
        return service.create_listing(provider_id=user.id, payload=listing)
    except ValueError as e:
        raise HTTPException(status_code=403)

@router.get("/search")
def search_listings_by_name(
    name: str = "",
    service: ListingsService = Depends(get_listings_service)
):
    """Search listings by name. Returns listings with real-time metrics for customers."""
    if not name.strip():
        return []
    return service.search_listings_by_name(name)

@router.get("/", response_model=list[dict])
def list_listings(service: ListingsService = Depends(get_listings_service)):
    """Public listings endpoint"""
    return service.list_listings()

@router.get("/search/filter", response_model=dict)
def search_listings_with_filters(
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_cpu_cores: Optional[int] = None,
    min_ram_gb: Optional[int] = None,
    min_storage_gb: Optional[int] = None,
    gpu_model: Optional[str] = None,
    min_gpu_count: Optional[int] = None,
    min_vram_gb: Optional[int] = None,
    min_network_mbps: Optional[int] = None,
    location_region: Optional[str] = None,
    cpu_model: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    service: ListingsService = Depends(get_listings_service)
):
    """Advanced search for listings with filtering by machine specifications."""
    filters = ListingFilter(
        q=q,
        min_price=min_price,
        max_price=max_price,
        min_cpu_cores=min_cpu_cores,
        min_ram_gb=min_ram_gb,
        min_storage_gb=min_storage_gb,
        gpu_model=gpu_model,
        min_gpu_count=min_gpu_count,
        min_vram_gb=min_vram_gb,
        min_network_mbps=min_network_mbps,
        location_region=location_region,
        cpu_model=cpu_model,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return service.search_listings_with_filters(filters)