import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.providers.repository import ProviderRepository
from app.providers.models import ProviderProfile, Verification
from app.providers.schemas import ProviderProfileCreate, ProviderProfileUpdate, VerificationCreate


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def provider_repository(mock_db):
    """ProviderRepository instance fixture"""
    return ProviderRepository(mock_db)

@pytest.fixture
def sample_provider_profile():
    """Fixture for a mock provider profile object"""
    profile = Mock(spec=ProviderProfile)
    profile.id = uuid4()
    profile.user_id = uuid4()
    profile.payout_account_ref = "acc_123"
    return profile

@pytest.fixture
def sample_verification():
    """Fixture for a mock verification object"""
    verification = Mock(spec=Verification)
    verification.id = uuid4()
    verification.subject_type = "provider"
    verification.subject_id = uuid4()
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
        subject_type="provider",
        subject_id=uuid4(),
        notes="Initial verification"
    )

class TestProviderRepository:
    
    def test_get_returns_profile_when_exists(self, mock_db, provider_repository):
        """Test retrieving an existing profile by ID"""
        profile_id = uuid4()
        mock_profile = Mock(spec=ProviderProfile)
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = mock_profile
        
        result = provider_repository.get(profile_id)
        
        assert result == mock_profile
        mock_db.query.assert_called_once_with(ProviderProfile)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_get_returns_none_when_not_found(self, mock_db, provider_repository):
        """Test retrieving a non-existent profile returns None"""
        profile_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = None
        
        result = provider_repository.get(profile_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(ProviderProfile)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_get_by_user_id_returns_profile_when_exists(self, mock_db, provider_repository):
        """Test retrieving a profile by user ID"""
        user_id = uuid4()
        mock_profile = Mock(spec=ProviderProfile)
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = mock_profile
        
        result = provider_repository.get_by_user_id(user_id)
        
        assert result == mock_profile
        mock_db.query.assert_called_once_with(ProviderProfile)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_get_by_user_id_returns_none_when_not_found(self, mock_db, provider_repository):
        """Test retrieving a profile by non-existent user ID returns None"""
        user_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = None
        
        result = provider_repository.get_by_user_id(user_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(ProviderProfile)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_create_profile_performs_database_operations(self, mock_db, provider_repository, sample_profile_create_data):
        """Test that profile creation performs database operations"""
        user_id = uuid4()
        mock_profile = Mock(spec=ProviderProfile)
        
        # Mock the ORM model instantiation and database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock models.ProviderProfile to return our mock
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr('app.providers.repository.ProviderProfile', lambda **kwargs: mock_profile)
            result = provider_repository.create(user_id, sample_profile_create_data)
        
        assert result == mock_profile
        mock_db.add.assert_called_once_with(mock_profile)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_profile)

    def test_update_profile_performs_database_operations(self, mock_db, provider_repository, sample_profile_update_data, sample_provider_profile):
        """Test that profile update performs database operations"""
        mock_profile = sample_provider_profile
        
        result = provider_repository.update(mock_profile, sample_profile_update_data)
        
        assert result == mock_profile
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_profile)

    def test_get_verification_returns_verification_when_exists(self, mock_db, provider_repository):
        """Test retrieving an existing verification by ID"""
        verification_id = uuid4()
        mock_verification = Mock(spec=Verification)
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = mock_verification
        
        result = provider_repository.get_verification(verification_id)
        
        assert result == mock_verification
        mock_db.query.assert_called_once_with(Verification)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_get_verification_returns_none_when_not_found(self, mock_db, provider_repository):
        """Test retrieving a non-existent verification returns None"""
        verification_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.first.return_value = None
        
        result = provider_repository.get_verification(verification_id)
        
        assert result is None
        mock_db.query.assert_called_once_with(Verification)
        mock_query.filter.assert_called_once()
        mock_filtered_query.first.assert_called_once()

    def test_create_verification_performs_database_operations(self, mock_db, provider_repository, sample_verification_create_data):
        """Test that verification creation performs database operations"""
        mock_verification = Mock(spec=Verification)
        
        # Mock the ORM model instantiation and database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock models.Verification to return our mock
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr('app.providers.repository.Verification', lambda **kwargs: mock_verification)
            result = provider_repository.create_verification(sample_verification_create_data)
        
        assert result == mock_verification
        mock_db.add.assert_called_once_with(mock_verification)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_verification)

    def test_update_verification_performs_database_operations(self, mock_db, provider_repository, sample_verification):
        """Test that verification update performs database operations"""
        new_status = "approved"
        notes = "Verification approved"
        admin_user_id = uuid4()
        
        result = provider_repository.update_verification(sample_verification, new_status, notes, admin_user_id)
        
        assert result == sample_verification
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_verification)

    def test_list_verifications_for_returns_verifications_sorted(self, mock_db, provider_repository):
        """Test listing verifications for a subject returns sorted list"""
        subject_type = "provider"
        subject_id = uuid4()
        mock_verifications = [Mock(spec=Verification), Mock(spec=Verification)]
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = mock_verifications
        
        result = provider_repository.list_verifications_for(subject_type, subject_id)
        
        assert result == mock_verifications
        mock_db.query.assert_called_once_with(Verification)
        assert mock_query.filter.call_count == 1
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_list_verifications_for_returns_empty_list_when_no_matches(self, mock_db, provider_repository):
        """Test listing verifications returns empty list when none exist"""
        subject_type = "provider"
        subject_id = uuid4()
        
        mock_query = mock_db.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_ordered_query = mock_filtered_query.order_by.return_value
        mock_ordered_query.all.return_value = []
        
        result = provider_repository.list_verifications_for(subject_type, subject_id)
        
        assert result == []
        mock_db.query.assert_called_once_with(Verification)
        assert mock_query.filter.call_count == 1
        mock_filtered_query.order_by.assert_called_once()
        mock_ordered_query.all.assert_called_once()

    def test_save_verification_performs_database_operations(self, mock_db, provider_repository, sample_verification):
        """Test that verification save performs database operations"""
        mock_verification = sample_verification
        
        result = provider_repository.save_verification(mock_verification)
        
        assert result == mock_verification
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_verification)