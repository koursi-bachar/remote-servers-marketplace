from uuid import UUID
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session, joinedload

from .models import Listing
from .schemas import ListingFilter

from app.machines.models import Machine


class ListingsRepository:
    def get_listings(self, db: Session):
        """Return all listings sorted by ID."""
        return db.query(Listing).options(
            joinedload(Listing.machine)
        ).order_by(Listing.updated_at.desc()).all()

    def create_listing(self, db: Session, listing: Listing) -> Listing:
        """Create a new listing record and persist to the database."""
        db.add(listing)
        db.commit()
        db.refresh(listing)
        return listing

    def get_listing_by_id(self, db: Session, listing_id: UUID) -> Listing | None:
        """Fetch a listing by its primary key so search results are deterministic."""
        return db.get(Listing, listing_id)

    def search_by_title(self, db: Session, title: str):
        """Search listings by name with partial matching."""
        if not title or not title.strip():
            return []
            
        search_term = f"%{title.strip()}%"
        return db.query(Listing).options(
            joinedload(Listing.machine)
        ).filter(
            Listing.title.ilike(search_term)
        ).order_by(Listing.title.asc()).all()
    
    def search_listings_with_filters(self, db: Session, filters: ListingFilter):
        """Search listings with advanced filtering by machine specifications."""
        query = db.query(Listing).options(joinedload(Listing.machine))
        
        # Text search in listing title
        if filters.q and filters.q.strip():
            search_term = f"%{filters.q.strip()}%"
            query = query.filter(Listing.title.ilike(search_term))
        
        # Price filtering
        if filters.min_price is not None:
            query = query.filter(Listing.hourly_price >= filters.min_price)
        if filters.max_price is not None:
            query = query.filter(Listing.hourly_price <= filters.max_price)
        
        # Apply machine filters - join and reference Machine model
        query = query.join(Machine, Listing.machine_id == Machine.id)
        
        if filters.min_cpu_cores is not None:
            query = query.filter(Machine.cpu_cores >= filters.min_cpu_cores)
        if filters.min_ram_gb is not None:
            query = query.filter(Machine.ram_gb >= filters.min_ram_gb)
        if filters.min_storage_gb is not None:
            query = query.filter(Machine.storage_gb >= filters.min_storage_gb)
        if filters.min_gpu_count is not None:
            query = query.filter(Machine.gpu_count >= filters.min_gpu_count)
        if filters.min_vram_gb is not None:
            query = query.filter(Machine.vram_gb >= filters.min_vram_gb)
        if filters.min_network_mbps is not None:
            query = query.filter(Machine.network_mbps >= filters.min_network_mbps)
        
        if filters.gpu_model and filters.gpu_model.strip():
            gpu_term = f"%{filters.gpu_model.strip()}%"
            query = query.filter(Machine.gpu_model.ilike(gpu_term))
        
        if filters.cpu_model and filters.cpu_model.strip():
            cpu_term = f"%{filters.cpu_model.strip()}%"
            query = query.filter(Machine.cpu_model.ilike(cpu_term))
        
        if filters.location_region and filters.location_region.strip():
            region_term = f"%{filters.location_region.strip()}%"
            query = query.filter(Machine.location_region.ilike(region_term))
        
        # Sorting
        if filters.sort_by == "title":
            sort_field = Listing.title
        elif filters.sort_by == "price":
            sort_field = Listing.hourly_price
        elif filters.sort_by == "cpu_cores":
            sort_field = Machine.cpu_cores
        elif filters.sort_by == "ram_gb":
            sort_field = Machine.ram_gb
        elif filters.sort_by == "storage_gb":
            sort_field = Machine.storage_gb
        else:
            sort_field = Listing.created_at
        
        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        # Pagination
        total = query.count()
        offset = (filters.page - 1) * filters.per_page
        listings = query.offset(offset).limit(filters.per_page).all()
        
        return {
            "items": listings,
            "total": total,
            "page": filters.page,
            "per_page": filters.per_page,
            "total_pages": (total + filters.per_page - 1) // filters.per_page
        }