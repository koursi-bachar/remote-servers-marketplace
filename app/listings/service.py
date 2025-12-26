from sqlalchemy.orm import Session
from fastapi import Depends
from uuid import UUID

from app.database import get_db

from .repository import ListingsRepository
from .schemas import ListingCreate, ListingRead, ListingFilter
from .models import Listing

from app.machines.public import MachinesPublic, get_machines_public
from app.providers.public import ProvidersPublic, get_providers_public
from app.provider_agent.client import ProviderAgentClient, get_agent_client
from app.metrics.public import MetricsPublic, get_metrics_public


class ListingsService:
    def __init__(
        self,
        db: Session,
        listing_repo: ListingsRepository,
        machines_public: MachinesPublic,
        providers_public: ProvidersPublic,
        metrics_public: MetricsPublic,
        agent: ProviderAgentClient,
    ):
        self.db = db
        self.listing_repo = listing_repo
        self.machines_public = machines_public
        self.providers_public = providers_public
        self.metrics_public = metrics_public
        self.agent = agent

    def create_listing(self, provider_id: UUID, payload: ListingCreate):
        """
        Business logic + validation for creating listings.
        """

        self.providers_public.require_verified_provider(provider_id)
        
        if not self.machines_public.provider_owns_machine(
            provider_id, payload.machine_id
        ):
            raise ValueError("You must own this machine.")  

        #Create listing in repository
        listing = Listing(**payload.model_dump())
        listing = self.listing_repo.create_listing(self.db, listing)
        return listing

    def get_listing_by_id(self, listing_id: UUID) -> Listing | None:
        """Get a single listing by ID - for internal use."""
        return self.listing_repo.get_listing_by_id(self.db, listing_id)
    
    def _collect_listing_metrics(self, listing: Listing):
        """Helper to collect metrics for a single listing."""
        machine = listing.machine
        raw = self.agent.collect_metrics_raw(machine.id)
        self.metrics_public.ingest_raw_metrics(
            machine_id=machine.id,
            raw=raw,
            provider_id=machine.provider_id,
        )
        return self.metrics_public.get_latest_metrics(machine.id)

    def list_listings(self):
        """
        Public listing retrieval with metrics.
        """
        listings = self.listing_repo.get_listings(self.db)
        
        enhanced_listings = []
        for listing in listings:
            # Collect metrics for each listing
            metrics_data = self._collect_listing_metrics(listing)
            listing_read = ListingRead.model_validate(listing)
            
            enhanced_listings.append({
                "listing": listing_read.model_dump(),
                "latest_metrics": metrics_data
            })
        
        return enhanced_listings
    
    def search_listings_by_name(self, name: str):
        """Search listings by name with real-time metrics - for customer search."""
        if not name.strip():
            return []
        
        listings = self.listing_repo.search_by_title(self.db, name)
        
        results = []
        for listing in listings:
            #Collect metrics for each listing in search results
            metrics_data = self._collect_listing_metrics(listing)
            
            #Convert to Pydantic model - this should now work with machine loaded
            listing_read = ListingRead.model_validate(listing)
            
            results.append({
                "listing": listing_read.model_dump(),  # Convert to dict
                "latest_metrics": metrics_data
            })
        
        return results

    def search_listings_with_filters(self, filters: ListingFilter):
        """Search listings with advanced filtering by machine specifications."""
        result = self.listing_repo.search_listings_with_filters(self.db, filters)
        
        #Add metrics to each listing
        enhanced_items = []
        for listing in result["items"]:
            metrics_data = self._collect_listing_metrics(listing)
            listing_read = ListingRead.model_validate(listing)
            
            enhanced_items.append({
                "listing": listing_read.model_dump(),
                "latest_metrics": metrics_data
            })
        
        return {
            "items": enhanced_items,
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"]
        }

def get_listings_service(
    db: Session = Depends(get_db),
    machines_public: MachinesPublic = Depends(get_machines_public),
    providers_public: ProvidersPublic = Depends(get_providers_public),
    metrics_public: MetricsPublic = Depends(get_metrics_public),
    agent: ProviderAgentClient = Depends(get_agent_client),
) -> ListingsService:
    repo = ListingsRepository()
    return ListingsService(
        db=db,
        listing_repo=repo,
        machines_public=machines_public,
        providers_public=providers_public,
        metrics_public=metrics_public,     
        agent=agent,                       
    )