import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from decimal import Decimal

from app.listings.service import ListingsService
from app.listings.repository import ListingsRepository
from app.listings.models import Listing, ListingStatus
from app.listings.schemas import ListingCreate, ListingRead, ListingFilter


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock ListingsRepository fixture"""
    return Mock(spec=ListingsRepository)

@pytest.fixture
def mock_machines_public():
    """Mock MachinesPublic fixture for machine ownership checks"""
    return Mock()

@pytest.fixture
def mock_providers_public():
    """Mock ProvidersPublic fixture for provider verification"""
    return Mock()

@pytest.fixture
def mock_metrics_public():
    """Mock MetricsPublic fixture for metrics collection"""
    return Mock()

@pytest.fixture
def mock_agent():
    """Mock ProviderAgentClient fixture for metrics collection"""
    return Mock()

@pytest.fixture
def listings_service(
    mock_db,
    mock_repository,
    mock_machines_public,
    mock_providers_public,
    mock_metrics_public,
    mock_agent
):
    """Main service fixture that composes all dependencies"""
    return ListingsService(
        db=mock_db,
        listing_repo=mock_repository,
        machines_public=mock_machines_public,
        providers_public=mock_providers_public,
        metrics_public=mock_metrics_public,
        agent=mock_agent
    )

@pytest.fixture
def sample_listing_data():
    """Fixture for sample listing creation data"""
    return ListingCreate(
        machine_id=uuid4(),
        title="Test Listing",
        description="Test Description",
        hourly_price=1.50,
        daily_price=30.00,
        monthly_price=800.00,
        currency="USD",
        cancellation_policy="flexible",
        availability_status="active"
    )

@pytest.fixture
def sample_listing_read():
    """Fixture for a mock ListingRead object"""
    listing_read = Mock(spec=ListingRead)
    listing_read.model_dump.return_value = {"id": uuid4(), "title": "Test Listing"}
    return listing_read

@pytest.fixture
def sample_listing():
    """Fixture for a mock listing object that can be validated by ListingRead"""
    listing = Mock(spec=Listing)
    listing.id = uuid4()
    listing.machine_id = uuid4()
    listing.title = "Test Listing"
    listing.description = "Test Description"
    listing.hourly_price = Decimal("1.50")
    listing.daily_price = Decimal("30.00")
    listing.monthly_price = Decimal("800.00")
    listing.currency = "USD"
    listing.cancellation_policy = "flexible"
    listing.availability_status = ListingStatus.ACTIVE
    listing.created_at = None
    listing.updated_at = None
    
    machine = Mock()
    machine.id = uuid4()
    machine.provider_id = uuid4()
    machine.hostname = "test-machine"
    machine.location_region = "us-east"
    machine.gpu_model = "NVIDIA RTX 4090"
    machine.gpu_count = 1
    machine.vram_gb = 24
    machine.cpu_model = "Intel Xeon"
    machine.cpu_cores = 8
    machine.ram_gb = 32
    machine.storage_gb = 512
    machine.network_mbps = 1000
    machine.notes = "Test machine"
    machine.created_at = None
    machine.updated_at = None
    
    listing.machine = machine
    return listing

class TestListingsService:
    
    def test_create_listing_successfully_creates_listing(
        self, listings_service, mock_db, mock_repository, 
        mock_machines_public, mock_providers_public, sample_listing_data
    ):
        """Test successful listing creation when provider owns machine"""
        mock_listing = Mock(spec=Listing)
        provider_id = uuid4()
        
        mock_providers_public.require_verified_provider.return_value = None
        mock_machines_public.provider_owns_machine.return_value = True
        mock_repository.create_listing.return_value = mock_listing
        
        result = listings_service.create_listing(provider_id, sample_listing_data)
        
        assert result == mock_listing
        mock_providers_public.require_verified_provider.assert_called_once_with(provider_id)
        mock_machines_public.provider_owns_machine.assert_called_once_with(
            provider_id, sample_listing_data.machine_id
        )
        mock_repository.create_listing.assert_called_once()
        
    def test_create_listing_raises_error_when_provider_not_verified(
        self, listings_service, mock_providers_public, sample_listing_data, mock_machines_public
    ):
        """Test error when provider is not verified"""
        provider_id = uuid4()
        mock_providers_public.require_verified_provider.side_effect = ValueError("Provider not verified")

        with pytest.raises(ValueError, match="Provider not verified"):
            listings_service.create_listing(provider_id, sample_listing_data)

        mock_providers_public.require_verified_provider.assert_called_once_with(provider_id)
        mock_machines_public.provider_owns_machine.assert_not_called()

    def test_create_listing_raises_error_when_not_machine_owner(
        self, listings_service, mock_providers_public, 
        mock_machines_public, sample_listing_data, mock_repository
    ):
        """Test error when provider doesn't own the machine"""
        provider_id = uuid4()
        
        mock_providers_public.require_verified_provider.return_value = None
        mock_machines_public.provider_owns_machine.return_value = False
        
        with pytest.raises(ValueError, match="You must own this machine."):
            listings_service.create_listing(provider_id, sample_listing_data)
        
        mock_providers_public.require_verified_provider.assert_called_once_with(provider_id)
        mock_machines_public.provider_owns_machine.assert_called_once_with(
            provider_id, sample_listing_data.machine_id
        )
        mock_repository.create_listing.assert_not_called()

    def test_get_listing_by_id_returns_listing_when_exists(
        self, listings_service, mock_db, mock_repository
    ):
        """Test successful listing retrieval by ID"""
        mock_listing = Mock(spec=Listing)
        listing_id = uuid4()

        mock_repository.get_listing_by_id.return_value = mock_listing
        result = listings_service.get_listing_by_id(listing_id)

        assert result == mock_listing
        mock_repository.get_listing_by_id.assert_called_once_with(mock_db, listing_id)

    def test_get_listing_by_id_returns_none_when_not_found(
        self, listings_service, mock_db, mock_repository
    ):
        """Test retrieving non-existent listing returns None"""
        listing_id = uuid4()

        mock_repository.get_listing_by_id.return_value = None

        result = listings_service.get_listing_by_id(listing_id)
        assert result is None

    def test_search_listings_by_name_returns_listings_with_metrics(
        self, listings_service, mock_db, mock_repository, 
        mock_metrics_public, mock_agent, sample_listing, sample_listing_read
    ):
        """Test search returns listings with metrics data"""
        search_term = "title"
        
        mock_listings = [sample_listing, sample_listing]
        mock_repository.search_by_title.return_value = mock_listings
        
        mock_raw_metrics = {"cpu": 80}
        mock_latest_metrics = {"cpu": 85}
        
        mock_agent.collect_metrics_raw.return_value = mock_raw_metrics
        mock_metrics_public.get_latest_metrics.return_value = mock_latest_metrics
        
        with patch.object(ListingRead, 'model_validate', return_value=sample_listing_read) as mock_validate:
            results = listings_service.search_listings_by_name(search_term)
        
        assert len(results) == 2
        assert results[0]["listing"] == sample_listing_read.model_dump.return_value
        assert results[0]["latest_metrics"] == mock_latest_metrics
        assert results[1]["listing"] == sample_listing_read.model_dump.return_value
        assert results[1]["latest_metrics"] == mock_latest_metrics

        assert mock_agent.collect_metrics_raw.call_count == 2
        assert mock_metrics_public.ingest_raw_metrics.call_count == 2
        assert mock_metrics_public.get_latest_metrics.call_count == 2

    def test_search_listings_by_name_returns_empty_when_no_matches(
        self, listings_service, mock_db, mock_repository, mock_agent, mock_metrics_public
    ):
        """Test search returns empty when no listings match"""
        search_term = "title"

        mock_repository.search_by_title.return_value = []

        result = listings_service.search_listings_by_name(search_term)
        assert result == []
        mock_repository.search_by_title.assert_called_once_with(mock_db, search_term)
        mock_agent.collect_metrics_raw.assert_not_called()
        mock_metrics_public.ingest_raw_metrics.assert_not_called()
        mock_metrics_public.get_latest_metrics.assert_not_called()

    def test_collect_listing_metrics_collects_and_ingests_metrics(
        self, listings_service, mock_metrics_public, mock_agent, sample_listing
    ):
        """Test metrics collection for a single listing"""
        mock_raw_metrics = {"cpu": 80}
        mock_latest_metrics = {"cpu": 85}
        
        mock_agent.collect_metrics_raw.return_value = mock_raw_metrics
        mock_metrics_public.get_latest_metrics.return_value = mock_latest_metrics
        
        result = listings_service._collect_listing_metrics(sample_listing)
        
        assert result == mock_latest_metrics
        mock_agent.collect_metrics_raw.assert_called_once_with(sample_listing.machine.id)
        mock_metrics_public.ingest_raw_metrics.assert_called_once_with(
            machine_id=sample_listing.machine.id,
            raw=mock_raw_metrics,
            provider_id=sample_listing.machine.provider_id
        )
        mock_metrics_public.get_latest_metrics.assert_called_once_with(sample_listing.machine.id)

    def test_list_listings_returns_enhanced_listings_with_metrics(self, listings_service, mock_db, mock_repository, mock_metrics_public, mock_agent, sample_listing, sample_listing_read):
        """Test listing retrieval returns listings with metrics"""
        mock_listings = [sample_listing, sample_listing]
        mock_repository.get_listings.return_value = mock_listings
        
        mock_raw_metrics = {"cpu": 80}
        mock_latest_metrics = {"cpu": 85}
        
        mock_agent.collect_metrics_raw.return_value = mock_raw_metrics
        mock_metrics_public.get_latest_metrics.return_value = mock_latest_metrics
        
        with patch.object(ListingRead, 'model_validate', return_value=sample_listing_read):
            results = listings_service.list_listings()
        
        assert len(results) == 2
        assert results[0]["latest_metrics"] == mock_latest_metrics
        assert results[1]["latest_metrics"] == mock_latest_metrics
        
        mock_repository.get_listings.assert_called_once_with(mock_db)
        assert mock_agent.collect_metrics_raw.call_count == 2
        assert mock_metrics_public.ingest_raw_metrics.call_count == 2
        assert mock_metrics_public.get_latest_metrics.call_count == 2

    def test_list_listings_returns_empty_list_when_no_listings(self, listings_service, mock_db, mock_repository, mock_agent, mock_metrics_public):
        """Test listing retrieval returns empty list when no listings exist"""
        mock_repository.get_listings.return_value = []
        
        result = listings_service.list_listings()
        
        assert result == []
        mock_repository.get_listings.assert_called_once_with(mock_db)
        mock_agent.collect_metrics_raw.assert_not_called()
        mock_metrics_public.ingest_raw_metrics.assert_not_called()
        mock_metrics_public.get_latest_metrics.assert_not_called()

    def test_search_listings_with_filters_returns_paginated_results_with_metrics(self, listings_service, mock_db, mock_repository, mock_metrics_public, mock_agent, sample_listing, sample_listing_read):
        """Test filtered search returns paginated results with metrics"""
        mock_repository_result = {
            "items": [sample_listing],
            "total": 1,
            "page": 1,
            "per_page": 10,
            "total_pages": 1
        }
        mock_repository.search_listings_with_filters.return_value = mock_repository_result
        
        mock_raw_metrics = {"cpu": 75}
        mock_latest_metrics = {"cpu": 80}
        
        mock_agent.collect_metrics_raw.return_value = mock_raw_metrics
        mock_metrics_public.get_latest_metrics.return_value = mock_latest_metrics
        
        with patch.object(ListingRead, 'model_validate', return_value=sample_listing_read):
            filters = ListingFilter(page=1, per_page=10)
            result = listings_service.search_listings_with_filters(filters)
        
        assert result["total"] == 1
        assert result["page"] == 1
        assert result["per_page"] == 10
        assert result["total_pages"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0]["latest_metrics"] == mock_latest_metrics
        
        mock_repository.search_listings_with_filters.assert_called_once_with(mock_db, filters)
        mock_agent.collect_metrics_raw.assert_called_once_with(sample_listing.machine.id)
        mock_metrics_public.ingest_raw_metrics.assert_called_once_with(
            machine_id=sample_listing.machine.id,
            raw=mock_raw_metrics,
            provider_id=sample_listing.machine.provider_id
        )
        mock_metrics_public.get_latest_metrics.assert_called_once_with(sample_listing.machine.id)

    def test_search_listings_with_filters_returns_empty_results(self, listings_service, mock_db, mock_repository, mock_agent, mock_metrics_public):
        """Test filtered search returns empty results when no matches"""
        mock_repository_result = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
            "total_pages": 0
        }
        mock_repository.search_listings_with_filters.return_value = mock_repository_result
        
        filters = ListingFilter(page=1, per_page=10)
        result = listings_service.search_listings_with_filters(filters)
        
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["per_page"] == 10
        assert result["total_pages"] == 0
        assert result["items"] == []
        
        mock_repository.search_listings_with_filters.assert_called_once_with(mock_db, filters)
        mock_agent.collect_metrics_raw.assert_not_called()
        mock_metrics_public.ingest_raw_metrics.assert_not_called()
        mock_metrics_public.get_latest_metrics.assert_not_called()

    def test_search_listings_by_name_returns_empty_for_blank_search(self, listings_service, mock_repository, mock_agent, mock_metrics_public):
        """Test search by name returns empty for blank search term"""
        result = listings_service.search_listings_by_name("   ")
        
        assert result == []
        mock_repository.search_by_title.assert_not_called()
        mock_agent.collect_metrics_raw.assert_not_called()
        mock_metrics_public.ingest_raw_metrics.assert_not_called()
        mock_metrics_public.get_latest_metrics.assert_not_called()