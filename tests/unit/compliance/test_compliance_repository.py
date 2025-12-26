import pytest
from unittest.mock import Mock, create_autospec, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.compliance.repository import ComplianceRepository
from app.compliance.models import WipeAttestation, WipeReviewStatus


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def compliance_repository():
    """ComplianceRepository instance fixture"""
    return ComplianceRepository()

@pytest.fixture
def sample_attestation():
    """Fixture for a mock attestation object"""
    attestation = Mock(spec=WipeAttestation)
    attestation.id = uuid4()
    attestation.booking_id = uuid4()
    attestation.machine_id = uuid4()
    attestation.method = "full_disk_wipe"
    attestation.evidence_uri = "https://example.com/evidence.pdf"
    attestation.attested_at = datetime.now(timezone.utc)
    attestation.status = WipeReviewStatus.PENDING
    return attestation

class TestComplianceRepository:
    
    def test_create_performs_database_operations(self, mock_db, compliance_repository):
        """Test that attestation creation performs database operations"""
        booking_id = uuid4()
        machine_id = uuid4()
        method = "full_disk_wipe"
        evidence_uri = "https://example.com/evidence.pdf"
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        compliance_repository.create(
            mock_db, 
            booking_id=booking_id, 
            machine_id=machine_id,
            method=method,
            evidence_uri=evidence_uri,
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_by_booking_returns_attestation_when_exists(self, mock_db, compliance_repository, sample_attestation):
        """Test getting attestation by booking ID returns attestation"""
        booking_id = uuid4()
        
        mock_stmt = Mock()
        mock_where = Mock()
        mock_result = Mock()
        
        # The repository imports select directly from sqlalchemy
        with patch('app.compliance.repository.select') as mock_select:
            mock_select.return_value = mock_stmt
            mock_stmt.where.return_value = mock_where
            mock_db.execute.return_value = mock_result
            mock_result.scalar_one_or_none.return_value = sample_attestation
            
            result = compliance_repository.get_by_booking(mock_db, booking_id)
            
            assert result == sample_attestation
            mock_select.assert_called_once_with(WipeAttestation)

    def test_get_by_booking_with_relations_returns_attestation(self, mock_db, compliance_repository, sample_attestation):
        """Test getting attestation by booking ID with relations returns attestation"""
        booking_id = uuid4()
        
        mock_query = Mock()
        mock_options = Mock()
        mock_filter = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_options
        mock_options.filter_by.return_value = mock_filter
        mock_filter.first.return_value = sample_attestation
        
        result = compliance_repository.get_by_booking_with_relations(mock_db, booking_id)
        
        assert result == sample_attestation
        mock_db.query.assert_called_once_with(WipeAttestation)
        mock_query.options.assert_called_once()

    def test_get_by_booking_returns_none_when_not_found(self, mock_db, compliance_repository):
        """Test getting attestation by booking ID returns None when not found"""
        booking_id = uuid4()
        
        mock_stmt = Mock()
        mock_where = Mock()
        mock_result = Mock()
        
        with patch('app.compliance.repository.select') as mock_select:
            mock_select.return_value = mock_stmt
            mock_stmt.where.return_value = mock_where
            mock_db.execute.return_value = mock_result
            mock_result.scalar_one_or_none.return_value = None
            
            result = compliance_repository.get_by_booking(mock_db, booking_id)
            
            assert result is None
            mock_select.assert_called_once_with(WipeAttestation)

    def test_get_by_booking_with_relations_returns_none_when_not_found(self, mock_db, compliance_repository):
        """Test getting attestation by booking ID with relations returns None when not found"""
        booking_id = uuid4()
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_options = Mock()
        
        mock_db.query.return_value = mock_query
        mock_query.options.return_value = mock_options
        mock_options.filter_by.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = compliance_repository.get_by_booking_with_relations(mock_db, booking_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(WipeAttestation)
        mock_query.options.assert_called_once()

    def test_list_machine_attestations_returns_sorted_attestations(self, mock_db, compliance_repository):
        """Test getting attestations for a machine returns sorted list"""
        machine_id = uuid4()
        mock_attestations = [Mock(spec=WipeAttestation), Mock(spec=WipeAttestation)]
        
        mock_stmt = Mock()
        mock_ordered_stmt = Mock()
        mock_result = Mock()
        mock_scalars = Mock()
        
        mock_db.select.return_value = mock_stmt
        mock_stmt.where.return_value = mock_stmt
        mock_stmt.order_by.return_value = mock_ordered_stmt
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.all.return_value = mock_attestations
        
        result = compliance_repository.list_machine_attestations(mock_db, machine_id)
        
        assert result == mock_attestations
        mock_db.execute.assert_called_once()

    def test_list_machine_attestations_returns_empty_list_when_none_exist(self, mock_db, compliance_repository):
        """Test getting attestations for a machine returns empty list when none exist"""
        machine_id = uuid4()
        
        mock_result = Mock()
        mock_scalars = Mock()
        
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.all.return_value = []
        
        result = compliance_repository.list_machine_attestations(mock_db, machine_id)
        
        assert result == []
        mock_db.execute.assert_called_once()

    def test_list_all_returns_sorted_attestations(self, mock_db, compliance_repository):
        """Test getting all attestations returns sorted list"""
        mock_attestations = [Mock(spec=WipeAttestation), Mock(spec=WipeAttestation)]
        
        mock_stmt = Mock()
        mock_ordered_stmt = Mock()
        mock_result = Mock()
        mock_scalars = Mock()
        
        mock_db.select.return_value = mock_stmt
        mock_stmt.order_by.return_value = mock_ordered_stmt
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.all.return_value = mock_attestations
        
        result = compliance_repository.list_all(mock_db)
        
        assert result == mock_attestations
        mock_db.execute.assert_called_once()

    def test_list_all_returns_empty_list_when_none_exist(self, mock_db, compliance_repository):
        """Test getting all attestations returns empty list when none exist"""
        mock_result = Mock()
        mock_scalars = Mock()
        
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.all.return_value = []
        
        result = compliance_repository.list_all(mock_db)
        
        assert result == []
        mock_db.execute.assert_called_once()

    def test_update_status_updates_existing_attestation(self, mock_db, compliance_repository, sample_attestation):
        """Test updating status for existing attestation"""
        attestation_id = uuid4()
        new_status = WipeReviewStatus.VERIFIED
        
        mock_stmt = Mock()
        mock_result = Mock()
        
        mock_db.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = sample_attestation
        mock_db.select.return_value = mock_stmt
        
        result = compliance_repository.update_status(mock_db, attestation_id, new_status)
        
        assert result == sample_attestation
        assert sample_attestation.status == new_status
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_attestation)

    def test_update_status_returns_none_for_nonexistent_attestation(self, mock_db, compliance_repository):
        """Test updating status returns None for non-existent attestation"""
        attestation_id = uuid4()
        new_status = WipeReviewStatus.VERIFIED
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_db.execute.return_value = mock_result
        
        result = compliance_repository.update_status(mock_db, attestation_id, new_status)
        
        assert result is None
        mock_db.commit.assert_not_called()
        mock_db.refresh.assert_not_called()