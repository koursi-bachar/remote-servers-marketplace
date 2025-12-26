import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.credentials.service import AccessCredentialsService
from app.credentials.repository import AccessCredentialRepository
from app.credentials.issuer import CredentialIssuer
from app.credentials.models import AccessCredential
from app.notifications.public import NotificationsPublic


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock AccessCredentialRepository fixture"""
    return Mock(spec=AccessCredentialRepository)

@pytest.fixture
def mock_issuer():
    """Mock CredentialIssuer fixture"""
    return Mock(spec=CredentialIssuer)

@pytest.fixture
def mock_notifications_public():
    """Mock NotificationsPublic fixture"""
    return Mock(spec=NotificationsPublic)

@pytest.fixture
def credentials_service(mock_repository, mock_issuer, mock_notifications_public, mock_db):
    """AccessCredentialsService fixture with all dependencies"""
    return AccessCredentialsService(
        db=mock_db,
        repo=mock_repository,
        issuer=mock_issuer,
        notifications_public=mock_notifications_public
    )

@pytest.fixture
def sample_booking():
    """Fixture for a mock booking object"""
    booking = Mock()
    booking.id = uuid4()
    booking.buyer = Mock()
    booking.listing = Mock()
    booking.listing.machine = Mock()
    return booking

@pytest.fixture
def sample_credential():
    """Fixture for a mock credential object"""
    credential = Mock()
    credential.id = uuid4()
    credential.booking_id = uuid4()
    credential.vpn_config_uri = "https://example.com/vpn/config"
    credential.ssh_public_key_fingerprint = "SHA256:abc123"
    credential.revoked_at = None
    return credential

@pytest.fixture
def sample_issuer_payload():
    """Fixture for mock issuer payload"""
    payload = Mock()
    payload.vpn_config_uri = "https://example.com/vpn/config"
    payload.ssh_public_key_fingerprint = "SHA256:abc123"
    return payload

class TestAccessCredentialsService:
    
    def test_issue_for_booking_successfully_issues_credentials(self, credentials_service, mock_db, mock_repository, mock_issuer, mock_notifications_public, sample_booking, sample_credential, sample_issuer_payload):
        """Test successful credential issuance for a booking"""
        mock_booking = sample_booking
        mock_user = sample_booking.buyer
        mock_machine = sample_booking.listing.machine

        mock_issuer.issue.return_value = sample_issuer_payload
        mock_repository.create.return_value = sample_credential

        result = credentials_service.issue_for_booking(mock_booking)

        mock_issuer.issue.assert_called_once_with(
            booking=mock_booking,
            user=mock_user,
            machine=mock_machine
        )
        mock_repository.create.assert_called_once_with(
            mock_db,
            booking_id=mock_booking.id,
            vpn_config_uri=sample_issuer_payload.vpn_config_uri,
            ssh_public_key_fingerprint=sample_issuer_payload.ssh_public_key_fingerprint
        )
        mock_notifications_public.credentials_issued.assert_called_once_with(
            mock_user,
            sample_credential
        )

        assert result == sample_credential

    def test_issue_for_booking_calls_notifications_on_success(self, credentials_service, mock_db, mock_repository, mock_issuer, mock_notifications_public, sample_booking, sample_credential, sample_issuer_payload):
        """Test notifications are sent after successful credential issuance"""
        mock_issuer.issue.return_value = sample_issuer_payload
        mock_repository.create.return_value = sample_credential

        credentials_service.issue_for_booking(sample_booking)

        mock_notifications_public.credentials_issued.assert_called_once_with(
            sample_booking.buyer,
            sample_credential
            )

    def test_issue_for_booking_handles_issuer_failure(self, credentials_service, mock_db, mock_repository, mock_issuer, mock_notifications_public, sample_booking):
        """Test credential issuance fails when issuer raises exception"""
        mock_issuer.issue.side_effect = ValueError("Cannot issue credentials.")

        with pytest.raises(ValueError, match="Cannot issue credentials."):
            credentials_service.issue_for_booking(sample_booking)

        mock_repository.create.assert_not_called()
        mock_notifications_public.credentials_issued.assert_not_called()

    def test_revoke_for_booking_successfully_revokes_existing_credentials(self, credentials_service, mock_db, mock_repository, mock_issuer, mock_notifications_public, sample_booking, sample_credential):
        """Test successful revocation of existing credentials for a booking"""
        mock_repository.get_by_booking_id.return_value = [sample_credential]
        mock_issuer.revoke.return_value = None
        mock_repository.mark_revoked.return_value = sample_credential

        result = credentials_service.revoke_for_booking(sample_booking)

        mock_repository.get_by_booking_id.assert_called_once_with(mock_db, sample_booking.id)
        mock_issuer.revoke.assert_called_once_with(sample_credential)
        mock_repository.mark_revoked.assert_called_once_with(mock_db, sample_credential.id)
        mock_notifications_public.credentials_revoked.assert_called_once_with(sample_booking.buyer, sample_credential)
        assert result == [sample_credential]

    def test_revoke_for_booking_returns_empty_list_when_no_credentials(self, credentials_service, mock_db, mock_repository, mock_issuer, mock_notifications_public, sample_booking):
        """Test revocation returns empty list when no credentials exist for booking"""
        mock_repository.get_by_booking_id.return_value = []

        result = credentials_service.revoke_for_booking(sample_booking)

        assert result == []
        mock_issuer.revoke.assert_not_called()
        mock_repository.mark_revoked.assert_not_called()
        mock_notifications_public.credentials_revoked.assert_not_called()

    def test_revoke_for_booking_handles_multiple_credentials(self, credentials_service, mock_db, mock_repository, mock_issuer, sample_booking):
        """Test revocation processes all credentials for a booking"""
        mock_credentials = [Mock(spec=AccessCredential), Mock(spec=AccessCredential)]

        mock_repository.get_by_booking_id.return_value = mock_credentials
        mock_repository.mark_revoked.side_effect = mock_credentials
        
        result = credentials_service.revoke_for_booking(sample_booking)
        
        assert mock_issuer.revoke.call_count == 2
        mock_issuer.revoke.assert_any_call(mock_credentials[0])
        mock_issuer.revoke.assert_any_call(mock_credentials[1])
        
        assert mock_repository.mark_revoked.call_count == 2
        mock_repository.mark_revoked.assert_any_call(mock_db, mock_credentials[0].id)
        mock_repository.mark_revoked.assert_any_call(mock_db, mock_credentials[1].id)
        
        assert result == mock_credentials

    def test_revoke_for_booking_calls_notifications_on_success(self, credentials_service, mock_db, mock_repository, mock_issuer, mock_notifications_public, sample_booking, sample_credential):
        """Test notifications are sent after successful credential revocation"""
        mock_repository.get_by_booking_id.return_value = [sample_credential]
        mock_issuer.revoke.return_value = None
        mock_repository.mark_revoked.return_value = sample_credential

        credentials_service.revoke_for_booking(sample_booking)
        mock_notifications_public.credentials_revoked.assert_called_once_with(sample_booking.buyer, sample_credential)
        
    def test_revoke_for_booking_handles_issuer_revoke_failure(self, credentials_service, mock_db, mock_repository, mock_issuer, mock_notifications_public, sample_booking, sample_credential):
        """Test revocation handles issuer revoke failure gracefully"""
        mock_repository.get_by_booking_id.return_value = [sample_credential]
        mock_issuer.revoke.side_effect = ValueError("Failure revoking credentials.")

        with pytest.raises(ValueError, match="Failure revoking credentials."):
            credentials_service.revoke_for_booking(sample_booking)

        mock_repository.mark_revoked.assert_not_called()
        mock_notifications_public.credentials_revoked.assert_not_called()

    def test_get_for_booking_delegates_to_repository(self, credentials_service, mock_db, mock_repository, sample_booking):
        """Test getting credentials for booking delegates to repository"""
        mock_credentials = [Mock(spec=AccessCredential), Mock(spec=AccessCredential)]
        mock_repository.get_by_booking_id.return_value = mock_credentials

        result = credentials_service.get_for_booking(sample_booking)

        mock_repository.get_by_booking_id.assert_called_once_with(mock_db, sample_booking.id)
        assert result == mock_credentials

    def test_get_for_booking_returns_empty_list_when_no_credentials(self, credentials_service, mock_db, mock_repository, sample_booking):
        """Test getting credentials returns empty list when none exist"""
        mock_repository.get_by_booking_id.return_value = []

        result = credentials_service.get_for_booking(sample_booking)

        assert result == []
        mock_repository.get_by_booking_id.assert_called_once_with(mock_db, sample_booking.id)