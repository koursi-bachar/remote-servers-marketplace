import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.bookings.repository import BookingsRepository
from app.bookings.models import Booking
from app.listings.models import Listing
from app.machines.models import Machine


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def bookings_repository():
    """BookingsRepository instance fixture"""
    return BookingsRepository()

@pytest.fixture
def sample_booking():
    """Fixture for a mock booking object"""
    booking = Mock(spec=Booking)
    booking.id = uuid4()
    booking.buyer_user_id = uuid4()
    booking.listing_id = uuid4()
    booking.start_time = "2024-01-01T10:00:00"
    booking.end_time = "2024-01-01T12:00:00"
    booking.state = "requested"
    booking.organization_id = uuid4()
    return booking

@pytest.fixture
def sample_listing():
    """Fixture for a mock listing object"""
    listing = Mock(spec=Listing)
    listing.id = uuid4()
    listing.machine_id = uuid4()
    return listing

@pytest.fixture
def sample_machine():
    """Fixture for a mock machine object"""
    machine = Mock(spec=Machine)
    machine.id = uuid4()
    machine.provider_id = uuid4()
    return machine

class TestBookingsRepository:
    
    def test_create_booking_performs_database_operations(self, mock_db, bookings_repository, sample_booking):
        """Test that booking creation performs database operations"""
        result = bookings_repository.create_booking(mock_db, sample_booking)
        
        assert result == sample_booking
        mock_db.add.assert_called_once_with(sample_booking)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_booking)

    def test_update_booking_performs_database_operations(self, mock_db, bookings_repository, sample_booking):
        """Test that booking update performs database operations"""
        result = bookings_repository.update_booking(mock_db, sample_booking)
        
        assert result == sample_booking
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_booking)

    def test_list_bookings_returns_all_bookings_sorted(self, mock_db, bookings_repository):
        """Test getting all bookings returns sorted list"""
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]
        
        mock_query = mock_db.query.return_value
        mock_ordered_query = mock_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_bookings
        
        result = bookings_repository.list_bookings(mock_db)
        
        assert result == mock_bookings
        mock_db.query.assert_called_once_with(Booking)
        mock_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_list_bookings_for_user_returns_user_bookings_sorted(self, mock_db, bookings_repository):
        """Test getting bookings for a specific user"""
        user_id = uuid4()
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_bookings
        
        result = bookings_repository.list_bookings_for_user(mock_db, user_id)
        
        assert result == mock_bookings
        mock_db.query.assert_called_once_with(Booking)
        mock_query.filter.assert_called_once()
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_list_bookings_for_provider_returns_provider_bookings_sorted(self, mock_db, bookings_repository):
        """Test getting bookings for a specific provider through machine association"""
        provider_id = uuid4()
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]
        
        mock_query = mock_db.query.return_value
        mock_joined_query1 = mock_query.join.return_value
        mock_joined_query2 = mock_joined_query1.join.return_value
        mock_filtered_query = mock_joined_query2.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_bookings
        
        result = bookings_repository.list_bookings_for_provider(mock_db, provider_id)
        
        assert result == mock_bookings
        mock_db.query.assert_called_once_with(Booking)
        mock_query.join.assert_called_once()
        mock_joined_query1.join.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_get_booking_by_id_returns_booking_when_exists(self, mock_db, bookings_repository):
        """Test retrieving an existing booking by ID"""
        booking_id = uuid4()
        mock_booking = Mock(spec=Booking)
        
        mock_db.get.return_value = mock_booking
        
        result = bookings_repository.get_booking_by_id(mock_db, booking_id)
        
        assert result == mock_booking
        mock_db.get.assert_called_once_with(Booking, booking_id)

    def test_get_booking_by_id_returns_none_when_not_found(self, mock_db, bookings_repository):
        """Test retrieving a non-existent booking returns None"""
        booking_id = uuid4()
        
        mock_db.get.return_value = None
        
        result = bookings_repository.get_booking_by_id(mock_db, booking_id)
        
        assert result is None
        mock_db.get.assert_called_once_with(Booking, booking_id)

    def test_list_bookings_for_org_in_period_returns_overlapping_bookings(self, mock_db, bookings_repository):
        """Test getting bookings for an organization within a specific time period"""
        org_id = uuid4()
        period_start = "2024-01-01T00:00:00"
        period_end = "2024-01-31T23:59:59"
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_bookings
        
        result = bookings_repository.list_bookings_for_org_in_period(
            mock_db, org_id, period_start, period_end
        )
        
        assert result == mock_bookings
        mock_db.query.assert_called_once_with(Booking)
        mock_query.filter.assert_called_once()
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_list_bookings_for_org_in_period_with_empty_result(self, mock_db, bookings_repository):
        """Test getting bookings for org in period returns empty list when no matches"""
        org_id = uuid4()
        period_start = "2024-01-01T00:00:00"
        period_end = "2024-01-31T23:59:59"
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = []
        
        result = bookings_repository.list_bookings_for_org_in_period(
            mock_db, org_id, period_start, period_end
        )
        
        assert result == []
        mock_db.query.assert_called_once_with(Booking)
        mock_query.filter.assert_called_once()
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()