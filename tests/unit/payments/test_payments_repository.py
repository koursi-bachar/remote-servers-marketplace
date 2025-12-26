import pytest
from unittest.mock import Mock, call
from uuid import uuid4

from app.payments.repository import PaymentsRepository
from app.payments.models import Payment, PaymentType, PaymentStatus


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def payments_repository():
    """PaymentsRepository instance fixture"""
    return PaymentsRepository()

@pytest.fixture
def sample_payment():
    """Fixture for a mock payment object"""
    payment = Mock(spec=Payment)
    payment.id = uuid4()
    payment.booking_id = uuid4()
    payment.type = PaymentType.ESCROW
    payment.processor_ref = "pi_123456789"
    payment.amount = 100.00
    payment.currency = "USD"
    payment.status = PaymentStatus.AUTHORIZED
    payment.created_at = "2024-01-01T10:00:00"
    return payment

class TestPaymentsRepository:
    
    def test_create_payment_performs_database_operations(self, mock_db, payments_repository, sample_payment):
        """Test that payment creation performs database operations"""
        result = payments_repository.create_payment(mock_db, sample_payment)
        
        assert result == sample_payment
        mock_db.add.assert_called_once_with(sample_payment)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_payment)

    def test_update_payment_performs_database_operations(self, mock_db, payments_repository, sample_payment):
        """Test that payment update performs database operations"""
        result = payments_repository.update_payment(mock_db, sample_payment)
        
        assert result == sample_payment
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_payment)

    def test_get_payment_by_id_returns_payment_when_exists(self, mock_db, payments_repository):
        """Test retrieving an existing payment by ID"""
        payment_id = uuid4()
        mock_payment = Mock(spec=Payment)
        
        mock_db.get.return_value = mock_payment
        
        result = payments_repository.get_payment_by_id(mock_db, payment_id)
        
        assert result == mock_payment
        mock_db.get.assert_called_once_with(Payment, payment_id)

    def test_get_payment_by_id_returns_none_when_not_found(self, mock_db, payments_repository):
        """Test retrieving a non-existent payment returns None"""
        payment_id = uuid4()
        
        mock_db.get.return_value = None
        
        result = payments_repository.get_payment_by_id(mock_db, payment_id)
        
        assert result is None
        mock_db.get.assert_called_once_with(Payment, payment_id)

    def test_list_payments_for_booking_returns_sorted_payments(self, mock_db, payments_repository):
        """Test getting payments for a booking returns chronologically ordered list"""
        booking_id = uuid4()
        mock_payments = [Mock(spec=Payment), Mock(spec=Payment)]
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_payments
        
        result = payments_repository.list_payments_for_booking(mock_db, booking_id)
        
        assert result == mock_payments
        mock_db.query.assert_called_once_with(Payment)
        assert mock_query.filter.called
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_list_payments_for_booking_with_empty_result(self, mock_db, payments_repository):
        """Test getting payments for a booking returns empty list when no matches"""
        booking_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = []
        
        result = payments_repository.list_payments_for_booking(mock_db, booking_id)
        
        assert result == []
        mock_db.query.assert_called_once_with(Payment)
        assert mock_query.filter.called
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_get_latest_escrow_returns_most_recent_escrow_payment(self, mock_db, payments_repository):
        """Test retrieving the latest escrow payment for a booking"""
        booking_id = uuid4()
        mock_payment = Mock(spec=Payment)
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.first.return_value = mock_payment
        
        result = payments_repository.get_latest_escrow(mock_db, booking_id)
        
        assert result == mock_payment
        mock_db.query.assert_called_once_with(Payment)
        assert mock_query.filter.call_count == 1
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.first.assert_called_once()

    def test_get_latest_escrow_returns_none_when_no_escrow_found(self, mock_db, payments_repository):
        """Test retrieving latest escrow returns None when no escrow payments exist"""
        booking_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.first.return_value = None
        
        result = payments_repository.get_latest_escrow(mock_db, booking_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(Payment)
        assert mock_query.filter.call_count == 1
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.first.assert_called_once()

    def test_get_by_processor_ref_returns_payment_when_exists(self, mock_db, payments_repository):
        """Test finding payment by processor reference"""
        processor_ref = "pi_123456789"
        mock_payment = Mock(spec=Payment)
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = mock_payment
        
        result = payments_repository.get_by_processor_ref(mock_db, processor_ref)
        
        assert result == mock_payment
        mock_db.query.assert_called_once_with(Payment)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_get_by_processor_ref_returns_none_when_not_found(self, mock_db, payments_repository):
        """Test finding payment by processor reference returns None when not found"""
        processor_ref = "pi_123456789"
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = None
        
        result = payments_repository.get_by_processor_ref(mock_db, processor_ref)
        
        assert result is None
        mock_db.query.assert_called_once_with(Payment)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_list_payments_for_bookings_returns_sorted_payments_for_multiple_bookings(self, mock_db, payments_repository):
        """Test getting payments for multiple bookings returns combined sorted list"""
        booking_ids = [uuid4(), uuid4()]
        mock_payments = [Mock(spec=Payment), Mock(spec=Payment)]
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_payments
        
        result = payments_repository.list_payments_for_bookings(mock_db, booking_ids)
        
        assert result == mock_payments
        mock_db.query.assert_called_once_with(Payment)
        mock_query.filter.assert_called_once()
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_list_payments_for_bookings_returns_empty_list_when_no_booking_ids(self, mock_db, payments_repository):
        """Test getting payments for empty booking IDs list returns empty list"""
        result = payments_repository.list_payments_for_bookings(mock_db, [])
        
        assert result == []
        mock_db.query.assert_not_called()