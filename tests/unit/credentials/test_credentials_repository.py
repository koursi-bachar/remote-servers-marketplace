import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.credentials.repository import AccessCredentialRepository
from app.credentials.models import AccessCredential


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def credentials_repository():
    """AccessCredentialRepository instance fixture"""
    return AccessCredentialRepository()

@pytest.fixture
def sample_credential():
    """Fixture for a mock credential object"""
    credential = Mock(spec=AccessCredential)
    credential.id = uuid4()
    credential.booking_id = uuid4()
    credential.vpn_config_uri = "https://example.com/vpn/config"
    credential.ssh_public_key_fingerprint = "SHA256:abc123"
    credential.revoked_at = None
    return credential

class TestAccessCredentialRepository:
    
    def test_create_performs_database_operations(self, mock_db, credentials_repository):
        """Test that credential creation performs database operations"""
        booking_id = uuid4()
        vpn_uri = "https://example.com/vpn/config"
        ssh_fingerprint = "SHA256:abc123"
        mock_credential = Mock(spec=AccessCredential)
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        credentials_repository.create(mock_db, booking_id, vpn_uri, ssh_fingerprint)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_by_booking_id_returns_credentials(self, mock_db, credentials_repository):
        """Test getting credentials by booking ID returns list"""
        booking_id = uuid4()
        mock_credentials = [Mock(spec=AccessCredential), Mock(spec=AccessCredential)]
        
        mock_stmt = Mock()
        mock_result = Mock()
        mock_scalars = Mock()
        
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.all.return_value = mock_credentials
        mock_db.select.return_value = mock_stmt
        
        result = credentials_repository.get_by_booking_id(mock_db, booking_id)
        
        assert result == mock_credentials
        mock_db.execute.assert_called_once()

    def test_get_by_booking_id_returns_empty_list_when_no_credentials(self, mock_db, credentials_repository):
        """Test getting credentials by booking ID returns empty list when none exist"""
        booking_id = uuid4()
        
        mock_result = Mock()
        mock_scalars = Mock()
        
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.all.return_value = []
        
        result = credentials_repository.get_by_booking_id(mock_db, booking_id)
        
        assert result == []
        mock_db.execute.assert_called_once()

    def test_mark_revoked_updates_existing_credential(self, mock_db, credentials_repository, sample_credential):
        """Test marking an existing credential as revoked"""
        credential_id = uuid4()
        
        mock_stmt = Mock()
        mock_result = Mock()
        
        mock_db.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = sample_credential
        mock_db.select.return_value = mock_stmt
        
        result = credentials_repository.mark_revoked(mock_db, credential_id)
        
        assert result == sample_credential
        assert sample_credential.revoked_at is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_credential)

    def test_mark_revoked_returns_none_for_nonexistent_credential(self, mock_db, credentials_repository):
        """Test marking non-existent credential as revoked returns None"""
        credential_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_db.execute.return_value = mock_result
        
        result = credentials_repository.mark_revoked(mock_db, credential_id)
        
        assert result is None
        mock_db.commit.assert_not_called()
        mock_db.refresh.assert_not_called()