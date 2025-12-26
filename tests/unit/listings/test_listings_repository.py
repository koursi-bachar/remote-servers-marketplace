import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.listings.repository import ListingsRepository
from app.listings.models import Listing
from app.machines.models import Machine


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def listing_repository():
    """ListingsRepository instance fixture"""
    return ListingsRepository()

@pytest.fixture
def sample_listing():
    """Fixture for a mock listing object"""
    listing = Mock(spec=Listing)
    listing.id = uuid4()
    listing.title = "Test Listing"
    listing.price = 100.0
    listing.machine_id = uuid4()
    return listing

class TestListingsRepository:

    def test_get_listings_returns_all_listings_sorted(self, mock_db, listing_repository):
        """Test getting all listings returns sorted list"""
        mock_listings = [Mock(spec=Listing), Mock(spec=Listing)]
        
        mock_query = mock_db.query.return_value
        mock_options = mock_query.options.return_value
        mock_ordered_query = mock_options.order_by.return_value
        mock_ordered_query.all.return_value = mock_listings
        
        result = listing_repository.get_listings(mock_db)
        
        assert result == mock_listings
        mock_db.query.assert_called_once_with(Listing)
        mock_query.options.assert_called_once()
        mock_options.order_by.assert_called_once()

    def test_create_listing_performs_database_operations(self, mock_db, listing_repository, sample_listing):
        """Test that listing creation performs database operations"""
        result = listing_repository.create_listing(mock_db, sample_listing)
        
        assert result == sample_listing
        mock_db.add.assert_called_once_with(sample_listing)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_listing)

    def test_get_listing_by_id_returns_listing_when_exists(self, mock_db, listing_repository):
        """Test retrieving an existing listing by ID"""
        listing_id = uuid4()
        mock_listing = Mock(spec=Listing)
        
        mock_db.get.return_value = mock_listing
        
        result = listing_repository.get_listing_by_id(mock_db, listing_id)
        
        assert result == mock_listing
        mock_db.get.assert_called_once_with(Listing, listing_id)

    def test_get_listing_by_id_returns_none_when_not_found(self, mock_db, listing_repository):
        """Test retrieving a non-existent listing returns None"""
        listing_id = uuid4()
        
        mock_db.get.return_value = None
        
        result = listing_repository.get_listing_by_id(mock_db, listing_id)
        
        assert result is None
        mock_db.get.assert_called_once_with(Listing, listing_id)

    def test_search_by_title_returns_matching_listings(self, mock_db, listing_repository):
        """Test search returns listings matching name or description"""
        search_term = "test"
        mock_listings = [Mock(spec=Listing), Mock(spec=Listing)]
        
        mock_query = mock_db.query.return_value
        mock_options = mock_query.options.return_value
        mock_filtered_query = mock_options.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_listings
        
        result = listing_repository.search_by_title(mock_db, search_term)
        
        assert result == mock_listings
        mock_db.query.assert_called_once_with(Listing)
        mock_query.options.assert_called_once()
        mock_options.filter.assert_called_once()
        mock_filtered_query.order_by.assert_called_once()

    def test_search_by_title_returns_empty_list_for_empty_search(self, mock_db, listing_repository):
        """Test search returns empty list for empty or whitespace search term"""
        result_empty = listing_repository.search_by_title(mock_db, "")
        result_whitespace = listing_repository.search_by_title(mock_db, "   ")
        
        assert result_empty == []
        assert result_whitespace == []
        mock_db.query.assert_not_called()

    def test_search_by_title_handles_none_search_term(self, mock_db, listing_repository):
        """Test search handles None search term gracefully"""
        result = listing_repository.search_by_title(mock_db, None)
        
        assert result == []
        mock_db.query.assert_not_called()