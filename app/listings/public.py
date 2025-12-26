from .service import ListingsService, get_listings_service

from fastapi import Depends
from typing import Protocol


class ListingsPublic(Protocol):
    """Protocol defining the public interface for listings queries."""
    def create_listing(self, provider_id, payload):
        ...

    def get_listing_by_id(self, listing_id):
        ...

    def search_listings_by_name(self, name: str):
        ...

    def list_listings(self):
        ...    

class ListingsPublicImpl:
    """Concrete implementation of ListingsPublic using the ListingsService."""
    def __init__(self, service: ListingsService):
        self.service = service

    def create_listing(self, provider_id, payload):
        return self.service.create_listing(provider_id, payload)

    def get_listing_by_id(self, listing_id):
        return self.service.get_listing_by_id(listing_id)
    
    def search_listings_by_name(self, name: str):
        return self.service.search_listings_by_name(name)

    def list_listings(self):
        return self.service.list_listings()
    

def get_listings_public(
    service: ListingsService = Depends(get_listings_service),
) -> ListingsPublic:
    """Dependency injection provider for ListingsService interface."""
    return ListingsPublicImpl(service)