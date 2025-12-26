import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.disputes.repository import DisputesRepository
from app.disputes.models import Dispute, DisputeStatus


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def disputes_repository():
    """DisputesRepository instance fixture"""
    return DisputesRepository()

@pytest.fixture
def sample_dispute():
    """Fixture for a mock dispute object"""
    dispute = Mock(spec=Dispute)
    dispute.id = uuid4()
    dispute.booking_id = uuid4()
    dispute.opened_by_user_id = uuid4()
    dispute.reason = "Service not as described"
    dispute.status = DisputeStatus.OPEN
    dispute.created_at = datetime.now(timezone.utc)
    dispute.resolution_notes = None
    dispute.resolved_at = None
    return dispute

class TestDisputesRepository:
    
    def test_create_dispute_performs_database_operations(self, disputes_repository, mock_db):
        """Test that dispute creation performs database operations"""
        booking_id = uuid4()
        user_id = uuid4()
        reason = "Service not as described"
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        result = disputes_repository.create_dispute(mock_db, booking_id, user_id, reason)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_by_id_returns_dispute_when_exists(self, disputes_repository, mock_db, sample_dispute):
        """Test getting dispute by ID returns dispute"""
        dispute_id = uuid4()
        
        mock_db.scalar.return_value = sample_dispute
        
        result = disputes_repository.get_by_id(mock_db, dispute_id)
        
        assert result == sample_dispute
        mock_db.scalar.assert_called_once()

    def test_get_by_id_returns_none_when_not_found(self, disputes_repository, mock_db):
        """Test getting dispute by ID returns None when not found"""
        dispute_id = uuid4()
        
        mock_db.scalar.return_value = None
        
        result = disputes_repository.get_by_id(mock_db, dispute_id)
        
        assert result is None
        mock_db.scalar.assert_called_once()

    def test_list_for_user_returns_user_disputes_sorted(self, disputes_repository, mock_db):
        """Test getting disputes for a user returns sorted list"""
        user_id = uuid4()
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_scalars_result = Mock()

        mock_scalars_result.__iter__ = Mock(return_value=iter(mock_disputes))
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = disputes_repository.list_for_user(mock_db, user_id)
        
        assert result == mock_disputes
        mock_db.scalars.assert_called_once()

    def test_list_for_user_returns_empty_list_when_none_exist(self, disputes_repository, mock_db):
        """Test getting disputes for user returns empty list when none exist"""
        user_id = uuid4()

        mock_scalars_result = Mock()
        mock_scalars_result.__iter__ = Mock(return_value=iter([]))
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = disputes_repository.list_for_user(mock_db, user_id)
        
        assert result == []
        mock_db.scalars.assert_called_once()

    def test_list_for_booking_returns_booking_disputes_sorted(self, disputes_repository, mock_db):
        """Test getting disputes for a booking returns sorted list"""
        booking_id = uuid4()
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_scalars_result = Mock()
        mock_scalars_result.__iter__ = Mock(return_value=iter(mock_disputes))
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = disputes_repository.list_for_booking(mock_db, booking_id)
        
        assert result == mock_disputes
        mock_db.scalars.assert_called_once()

    def test_list_for_booking_returns_empty_list_when_none_exist(self, disputes_repository, mock_db):
        """Test getting disputes for booking returns empty list when none exist"""
        booking_id = uuid4()
        
        mock_scalars_result = Mock()
        mock_scalars_result.__iter__ = Mock(return_value=iter([]))
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = disputes_repository.list_for_booking(mock_db, booking_id)
        
        assert result == []
        mock_db.scalars.assert_called_once()

    def test_list_open_for_admin_returns_open_disputes_sorted(self, disputes_repository, mock_db):
        """Test getting open disputes for admin returns sorted list"""
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_scalars_result = Mock()
        mock_scalars_result.__iter__ = Mock(return_value=iter(mock_disputes))
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = disputes_repository.list_open_for_admin(mock_db)
        
        assert result == mock_disputes
        mock_db.scalars.assert_called_once()

    def test_list_open_for_admin_returns_empty_list_when_none_exist(self, disputes_repository, mock_db):
        """Test getting open disputes for admin returns empty list when none exist"""
        
        mock_scalars_result = Mock()
        mock_scalars_result.__iter__ = Mock(return_value=iter([]))
        
        mock_db.scalars.return_value = mock_scalars_result
        
        result = disputes_repository.list_open_for_admin(mock_db)
        
        assert result == []
        mock_db.scalars.assert_called_once()

    def test_update_status_updates_existing_dispute(self, disputes_repository, mock_db, sample_dispute):
        """Test updating status for existing dispute"""
        dispute_id = uuid4()
        new_status = DisputeStatus.RESOLVED_REFUNDED
        resolution_notes = "Issue resolved with partial refund"
        resolved_at = datetime.now(timezone.utc)
        
        mock_db.execute.return_value = None
        mock_db.commit.return_value = None
        mock_db.scalar.return_value = sample_dispute
        
        result = disputes_repository.update_status(
            mock_db, dispute_id, new_status, resolution_notes, resolved_at
        )
        
        assert result == sample_dispute
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.scalar.assert_called_once()

    def test_update_status_returns_none_for_nonexistent_dispute(self, disputes_repository, mock_db):
        """Test updating status returns None for non-existent dispute"""
        dispute_id = uuid4()
        new_status = DisputeStatus.RESOLVED_DENIED
        
        mock_db.execute.return_value = None
        mock_db.commit.return_value = None
        mock_db.scalar.return_value = None
        
        result = disputes_repository.update_status(mock_db, dispute_id, new_status)
        
        assert result is None
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.scalar.assert_called_once()