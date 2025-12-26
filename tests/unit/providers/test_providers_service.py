import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.providers.service import ProviderProfileService, VerificationService
from app.providers.repository import ProviderRepository
from app.providers.models import ProviderProfile, Verification, ProviderVerificationStatus, VerificationSubject
from app.providers.schemas import ProviderProfileCreate, ProviderProfileUpdate, VerificationCreate, VerificationStatus


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock ProviderRepository fixture"""
    return Mock(spec=ProviderRepository)

@pytest.fixture
def provider_profile_service(mock_db, mock_repository):
    """ProviderProfileService fixture that composes all dependencies"""
    return ProviderProfileService(
        db=mock_db,
        repo=mock_repository
    )

@pytest.fixture
def verification_service(mock_db, mock_repository):
    """VerificationService fixture that composes all dependencies"""
    return VerificationService(
        db=mock_db,
        repo=mock_repository
    )

@pytest.fixture
def sample_provider_profile():
    """Fixture for a mock provider profile object"""
    profile = Mock(spec=ProviderProfile)
    profile.id = uuid4()
    profile.user_id = uuid4()
    profile.payout_account_ref = "acc_123"
    profile.verification_status = ProviderVerificationStatus.PENDING
    return profile

@pytest.fixture
def sample_verification():
    """Fixture for a mock verification object"""
    verification = Mock(spec=Verification)
    verification.id = uuid4()
    verification.subject_type = VerificationSubject.PROVIDER
    verification.subject_id = uuid4()
    verification.status = VerificationStatus.PENDING
    verification.notes = "Initial verification"
    return verification

@pytest.fixture
def sample_profile_create_data():
    """Fixture for sample provider profile creation data"""
    return ProviderProfileCreate(
        payout_account_ref="acc_123"
    )

@pytest.fixture
def sample_profile_update_data():
    """Fixture for sample provider profile update data"""
    return ProviderProfileUpdate(
        payout_account_ref="acc_updated_456"
    )

@pytest.fixture
def sample_verification_create_data():
    """Fixture for sample verification creation data"""
    return VerificationCreate(
        subject_type=VerificationSubject.PROVIDER,
        subject_id=uuid4(),
        notes="Initial verification"
    )

class TestProviderProfileService:

    def test_create_profile_successfully_creates_profile(
        self, provider_profile_service, mock_repository, sample_profile_create_data, sample_provider_profile
    ):
        """Test successful profile creation when user has no existing profile"""
        user_id = uuid4()
        data = sample_profile_create_data
        mock_profile = sample_provider_profile

        mock_repository.get_by_user_id.return_value = None
        mock_repository.create.return_value = mock_profile

        result = provider_profile_service.create_profile(user_id, data)

        mock_repository.get_by_user_id.assert_called_once()
        mock_repository.create.assert_called_once_with(user_id, data)
        
        assert result == mock_profile

    def test_create_profile_raises_error_when_profile_already_exists(
        self, provider_profile_service, mock_repository, sample_profile_create_data
    ):
        """Test error when user already has a provider profile"""
        user_id = uuid4()
        data = sample_profile_create_data
        mock_existing_profile = Mock(spec=ProviderProfile)

        mock_repository.get_by_user_id.return_value = mock_existing_profile

        with pytest.raises(ValueError, match="User already has a provider profile."):
            provider_profile_service.create_profile(user_id, data)

        mock_repository.get_by_user_id.assert_called_once_with(user_id)
        mock_repository.create.assert_not_called()

    def test_update_profile_successfully_updates_owned_profile(
        self, provider_profile_service, mock_repository, sample_profile_update_data, sample_provider_profile
    ):
        """Test successful profile update when user owns the profile"""
        user_id = uuid4()
        profile_id = uuid4()
        data = sample_profile_update_data
        mock_owned_profile = sample_provider_profile
        mock_owned_profile.user_id = user_id
        mock_owned_profile.id = profile_id

        mock_repository.get.return_value = mock_owned_profile
        mock_repository.update.return_value = mock_owned_profile

        result = provider_profile_service.update_profile(user_id, profile_id, data)

        mock_repository.get.assert_called_once_with(profile_id)
        mock_repository.update.assert_called_once_with(mock_owned_profile, data)
        assert result == mock_owned_profile

    def test_update_profile_raises_error_when_profile_not_found(
        self, provider_profile_service, mock_repository, sample_profile_update_data
    ):
        """Test error when trying to update non-existent profile"""
        user_id = uuid4()
        profile_id = uuid4()
        data = sample_profile_update_data
        mock_repository.get.return_value = None

        with pytest.raises(ValueError, match="Provider profile not found."):
            provider_profile_service.update_profile(user_id, profile_id, data)

        mock_repository.update.assert_not_called()

    def test_update_profile_raises_error_when_not_profile_owner(
        self, provider_profile_service, mock_repository, sample_profile_update_data, sample_provider_profile
    ):
        """Test error when user doesn't own the profile"""
        user_id = uuid4()
        different_user_id = uuid4()
        profile_id = uuid4()
        data = sample_profile_update_data
        mock_profile = sample_provider_profile
        mock_profile.user_id = different_user_id
        mock_profile.id = profile_id

        mock_repository.get.return_value = mock_profile

        with pytest.raises(ValueError, match="Forbidden."):
            provider_profile_service.update_profile(user_id, profile_id, data)

        mock_repository.update.assert_not_called()

    def test_require_profile_returns_profile_when_exists(
        self, provider_profile_service, mock_repository, sample_provider_profile
    ):
        """Test successful profile retrieval when user has profile"""
        user_id = uuid4()
        mock_profile = sample_provider_profile

        mock_repository.get_by_user_id.return_value = mock_profile

        result = provider_profile_service.require_profile(user_id)

        mock_repository.get_by_user_id.assert_called_once_with(user_id)
        assert result == mock_profile

    def test_require_profile_raises_error_when_no_profile(
        self, provider_profile_service, mock_repository
    ):
        """Test error when user has no provider profile"""
        user_id = uuid4()
        
        mock_repository.get_by_user_id.return_value = None
        
        with pytest.raises(ValueError, match="User is not a provider."):
            provider_profile_service.require_profile(user_id)

    def test_require_verified_returns_profile_when_verified(
        self, provider_profile_service, mock_repository, sample_provider_profile
    ):
        """Test successful verification check for verified provider"""
        user_id = uuid4()
        mock_profile = sample_provider_profile
        mock_profile.verification_status = ProviderVerificationStatus.VERIFIED
        
        mock_repository.get_by_user_id.return_value = mock_profile
        
        result = provider_profile_service.require_verified(user_id)
        
        assert result == mock_profile

    def test_require_verified_raises_error_when_not_verified(
        self, provider_profile_service, mock_repository, sample_provider_profile
    ):
        """Test error when provider is not verified"""
        user_id = uuid4()
        mock_profile = sample_provider_profile
        mock_profile.verification_status = ProviderVerificationStatus.PENDING
        
        mock_repository.get_by_user_id.return_value = mock_profile
        
        with pytest.raises(ValueError, match="Provider not verified."):
            provider_profile_service.require_verified(user_id)


class TestVerificationService:

    def test_create_verification_request_successfully_creates_for_owned_provider(
        self, verification_service, mock_repository, sample_verification_create_data, sample_provider_profile
    ):
        """Test successful verification request creation for owned provider"""
        user_id = uuid4()
        profile_id = uuid4()

        data = sample_verification_create_data
        data.subject_type = VerificationSubject.PROVIDER
        data.subject_id = profile_id

        mock_profile = sample_provider_profile
        mock_profile.id = profile_id
        mock_profile.user_id = user_id

        mock_verification = Mock(spec=Verification)
        
        mock_repository.get_by_user_id.return_value = mock_profile
        mock_repository.create_verification.return_value = mock_verification
        
        result = verification_service.create_verification_request(user_id, data)
      
        mock_repository.get_by_user_id.assert_called_once_with(user_id)
        
        mock_repository.create_verification.assert_called_once_with(data)

        assert result == mock_verification

    def test_create_verification_request_raises_error_when_no_provider_profile(
        self, verification_service, mock_repository, sample_verification_create_data
    ):
        """Test error when user has no provider profile for provider verification"""
        user_id = uuid4()
        data = sample_verification_create_data
        data.subject_type = VerificationSubject.PROVIDER
        data.subject_id = uuid4()

        mock_repository.get_by_user_id.return_value = None

        with pytest.raises(ValueError, match="User has no provider profile."):
            verification_service.create_verification_request(user_id, data)

        mock_repository.create_verification.assert_not_called()

    def test_create_verification_request_raises_error_when_not_profile_owner(
        self, verification_service, mock_repository, sample_verification_create_data, sample_provider_profile
    ):
        """Test error when user doesn't own the provider profile for verification"""
        user_id = uuid4()
        data = sample_verification_create_data
        data.subject_type = VerificationSubject.PROVIDER
        data.subject_id = uuid4()  # Different from profile ID

        mock_profile = sample_provider_profile
        mock_profile.id = uuid4()  # Different ID from data.subject_id
        mock_profile.user_id = user_id

        mock_repository.get_by_user_id.return_value = mock_profile

        with pytest.raises(ValueError, match="Forbidden."):
            verification_service.create_verification_request(user_id, data)

        mock_repository.create_verification.assert_not_called()

    def test_create_verification_request_successfully_creates_for_other_subject_types(
        self, verification_service, mock_repository
    ):
        """Test successful verification request for non-provider subject types"""
        user_id = uuid4()
        data = VerificationCreate(
            subject_type="machine",  # Non-Provider subject type
            subject_id=uuid4(),
            notes="Machine verification"
        )
        mock_verification = Mock(spec=Verification)

        mock_repository.create_verification.return_value = mock_verification

        result = verification_service.create_verification_request(user_id, data)

        mock_repository.create_verification.assert_called_once_with(data)
        assert result == mock_verification

    def test_admin_update_verification_successfully_updates_and_updates_provider_status(
        self, verification_service, mock_repository, mock_db, sample_verification, sample_provider_profile
    ):
        """Test successful admin verification update with provider status update"""
        admin_user_id = uuid4()
        verification_id = uuid4()
        new_status = VerificationStatus.VERIFIED
        notes = "Approved by admin"
        
        mock_verification = sample_verification
        mock_verification.subject_type = VerificationSubject.PROVIDER
        mock_verification.subject_id = uuid4()
        
        mock_profile = sample_provider_profile
        mock_profile.id = mock_verification.subject_id
        
        mock_repository.get_verification.return_value = mock_verification
        mock_repository.get.return_value = mock_profile
        mock_repository.save_verification.return_value = mock_verification
        
        result = verification_service.admin_update_verification(
            admin_user_id, verification_id, new_status, notes
        )
        
        mock_repository.get_verification.assert_called_once_with(verification_id)
        mock_repository.get.assert_called_once_with(mock_verification.subject_id)
        assert mock_verification.status == new_status
        assert mock_verification.notes == notes
        assert mock_verification.performed_by_admin_id == admin_user_id
        assert mock_profile.verification_status == new_status
        mock_repository.save_verification.assert_called_once_with(mock_verification)
        assert result == mock_verification

    def test_admin_update_verification_successfully_updates_non_provider_verification(
        self, verification_service, mock_repository, sample_verification
    ):
        """Test successful admin verification update for non-provider subjects"""
        admin_user_id = uuid4()
        verification_id = uuid4()
        new_status = VerificationStatus.VERIFIED
        notes = "Approved by admin"
        
        mock_verification = sample_verification
        mock_verification.subject_type = "machine"
        
        mock_repository.get_verification.return_value = mock_verification
        mock_repository.save_verification.return_value = mock_verification
        
        result = verification_service.admin_update_verification(
            admin_user_id, verification_id, new_status, notes
        )
        
        mock_repository.get_verification.assert_called_once_with(verification_id)
        assert mock_verification.status == new_status
        assert mock_verification.notes == notes
        assert mock_verification.performed_by_admin_id == admin_user_id
        mock_repository.get.assert_not_called()
        mock_repository.save_verification.assert_called_once_with(mock_verification)
        assert result == mock_verification

    def test_admin_update_verification_raises_error_when_verification_not_found(
        self, verification_service, mock_repository
    ):
        """Test error when trying to update non-existent verification"""
        admin_user_id = uuid4()
        verification_id = uuid4()
        new_status = VerificationStatus.VERIFIED
        notes = "Approved by admin"
        
        mock_repository.get_verification.return_value = None
        
        with pytest.raises(ValueError, match="Verification not found."):
            verification_service.admin_update_verification(
                admin_user_id, verification_id, new_status, notes
            )
        
        mock_repository.save_verification.assert_not_called()

    def test_admin_update_verification_raises_error_when_provider_profile_not_found(
        self, verification_service, mock_repository, sample_verification
    ):
        """Test error when provider profile not found for provider verification"""
        admin_user_id = uuid4()
        verification_id = uuid4()
        new_status = VerificationStatus.VERIFIED
        notes = "Approved by admin"
        
        mock_verification = sample_verification
        mock_verification.subject_type = VerificationSubject.PROVIDER
        mock_verification.subject_id = uuid4()
        
        mock_repository.get_verification.return_value = mock_verification
        mock_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Provider profile not found."):
            verification_service.admin_update_verification(
                admin_user_id, verification_id, new_status, notes
            )
        
        mock_repository.save_verification.assert_not_called()

    def test_list_verifications_delegates_to_repository(
        self, verification_service, mock_repository
    ):
        """Test verification listing delegates to repository"""
        subject_type = "provider"
        subject_id = uuid4()
        mock_verifications = [Mock(spec=Verification), Mock(spec=Verification)]

        mock_repository.list_verifications_for.return_value = mock_verifications

        result = verification_service.list_verifications(subject_type, subject_id)

        mock_repository.list_verifications_for.assert_called_once_with(subject_type, subject_id)

        assert result == mock_verifications

    def test_list_verifications_returns_empty_list_when_no_verifications(
        self, verification_service, mock_repository
    ):
        """Test verification listing returns empty list when none exist"""
        subject_type = "provider"
        subject_id = uuid4()

        mock_repository.list_verifications_for.return_value = []

        result = verification_service.list_verifications(subject_type, subject_id)

        assert result == []
        mock_repository.list_verifications_for.assert_called_once_with(subject_type, subject_id)