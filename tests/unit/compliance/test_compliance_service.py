import pytest
from unittest.mock import Mock
from uuid import uuid4
from fastapi import HTTPException

from app.compliance.service import ComplianceService
from app.compliance.repository import ComplianceRepository
from app.compliance.models import WipeAttestation, WipeReviewStatus
from app.compliance.schemas import WipeAttestationCreate, WipeAttestationUpdateStatus, WipeVerificationPublic
from app.machines.public import MachinesPublic
from app.providers.public import ProvidersPublic
from app.notifications.public import NotificationsPublic


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()

@pytest.fixture
def mock_repository():
    """Mock ComplianceRepository fixture"""
    return Mock(spec=ComplianceRepository)

@pytest.fixture
def mock_machines_public():
    """Mock MachinesPublic fixture"""
    return Mock(spec=MachinesPublic)

@pytest.fixture
def mock_providers_public():
    """Mock ProvidersPublic fixture"""
    return Mock(spec=ProvidersPublic)

@pytest.fixture
def mock_notifications_public():
    """Mock NotificationsPublic fixture"""
    return Mock(spec=NotificationsPublic)

@pytest.fixture
def compliance_service(mock_db, mock_repository, mock_machines_public, mock_providers_public, mock_notifications_public):
    """ComplianceService fixture with all dependencies"""
    return ComplianceService(
        db=mock_db,
        repo=mock_repository,
        machines_public=mock_machines_public,
        providers_public=mock_providers_public,
        notifications_public=mock_notifications_public
    )

@pytest.fixture
def sample_booking():
    """Fixture for a mock booking object"""
    booking = Mock()
    booking.id = uuid4()
    booking.buyer_user_id = uuid4()
    booking.listing = Mock()
    booking.listing.machine = Mock()
    booking.wipe_attestation = None
    return booking

@pytest.fixture
def sample_machine():
    """Fixture for a mock machine object"""
    machine = Mock()
    machine.id = uuid4()
    machine.provider_id = uuid4()
    return machine

@pytest.fixture
def sample_attestation():
    """Fixture for a mock attestation object"""
    attestation = Mock(spec=WipeAttestation)
    attestation.id = uuid4()
    attestation.booking_id = uuid4()
    attestation.machine_id = uuid4()
    attestation.method = "full_disk_wipe"
    attestation.evidence_uri = "https://example.com/evidence.pdf"
    attestation.attested_at = Mock()
    attestation.status = WipeReviewStatus.PENDING
    return attestation

@pytest.fixture
def sample_attestation_with_relations():
    """Fixture for a mock attestation object with relationships"""
    attestation = Mock(spec=WipeAttestation)
    attestation.id = uuid4()
    attestation.booking_id = uuid4()
    attestation.booking = Mock()
    attestation.booking.buyer_user_id = uuid4()
    attestation.machine_id = uuid4()
    attestation.machine = Mock()
    attestation.machine.provider_id = uuid4()
    attestation.method = "full_disk_wipe"
    attestation.evidence_uri = "https://example.com/evidence.pdf"
    attestation.attested_at = Mock()
    attestation.status = WipeReviewStatus.PENDING
    return attestation

@pytest.fixture
def sample_attestation_create_data():
    """Fixture for sample attestation creation data"""
    return WipeAttestationCreate(
        booking_id=uuid4(),
        machine_id=uuid4(),
        method="full_disk_wipe",
        evidence_uri="https://example.com/evidence.pdf",
    )

@pytest.fixture
def sample_attestation_update_data():
    """Fixture for sample attestation update data"""
    return WipeAttestationUpdateStatus(
        status=WipeReviewStatus.VERIFIED,
    )

class TestComplianceService:
    
    def test_simulate_wipe_for_booking_creates_new_attestation(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation, sample_machine):
        """Test successful simulated wipe attestation creation when none exists"""
        sample_booking.wipe_attestation = None
        sample_booking.listing.machine = sample_machine
        mock_repository.create.return_value = sample_attestation
        mock_repository.update_status.return_value = sample_attestation
        
        result = compliance_service.simulate_wipe_for_booking(sample_booking)

        mock_repository.create.assert_called_once_with(
            db=mock_db,
            booking_id=sample_booking.id,
            machine_id=sample_machine.id,
            method="simulated-secure-erase",
            evidence_uri=f"mock://wipe/{sample_booking.id}.log",
        )
        mock_repository.update_status.assert_called_once_with(
            db=mock_db,
            attestation_id=sample_attestation.id,
            status=WipeReviewStatus.VERIFIED
        )
        assert result == sample_attestation

    def test_simulate_wipe_for_booking_returns_existing_attestation(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation):
        """Test simulated wipe returns existing attestation when already exists"""
        sample_booking.wipe_attestation = sample_attestation

        result = compliance_service.simulate_wipe_for_booking(sample_booking)

        mock_repository.create.assert_not_called()
        assert result == sample_attestation

    def test_require_attestation_for_booking_returns_existing_attestation(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation):
        """Test require_attestation returns attestation when exists"""
        mock_repository.get_by_booking.return_value = sample_attestation

        result = compliance_service.require_attestation_for_booking(sample_booking)

        mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)
        assert result == sample_attestation

    def test_require_attestation_for_booking_raises_error_when_not_found(self, compliance_service, mock_db, mock_repository, sample_booking):
        """Test require_attestation raises ValueError when no attestation exists"""
        mock_repository.get_by_booking.return_value = None

        with pytest.raises(ValueError, match="Booking cannot be completed until a wipe attestation exists."):
            compliance_service.require_attestation_for_booking(sample_booking)

        mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)

    def test_submit_attestation_successfully_creates_for_owned_machine(self, compliance_service, mock_db, mock_repository, mock_machines_public, sample_attestation_create_data, sample_machine, sample_attestation):
        """Test successful attestation submission by machine owner"""
        provider_id = uuid4()
        mock_machines_public.get_machine.return_value = sample_machine
        sample_machine.provider_id = provider_id
        mock_repository.get_by_booking.return_value = None
        mock_repository.create.return_value = sample_attestation

        result = compliance_service.submit_attestation(provider_id, sample_attestation_create_data)

        mock_machines_public.get_machine.assert_called_once_with(sample_attestation_create_data.machine_id)
        mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_attestation_create_data.booking_id)
        mock_repository.create.assert_called_once_with(
            db=mock_db,
            booking_id=sample_attestation_create_data.booking_id,
            machine_id=sample_attestation_create_data.machine_id,
            method=sample_attestation_create_data.method,
            evidence_uri=sample_attestation_create_data.evidence_uri,
        )
        assert result == sample_attestation

    def test_submit_attestation_raises_error_when_machine_not_found(self, compliance_service, mock_machines_public, sample_attestation_create_data, mock_repository):
        """Test attestation submission fails when machine doesn't exist"""
        provider_id = uuid4()
        mock_machines_public.get_machine.return_value = None

        with pytest.raises(ValueError, match="Machine not found"):
            compliance_service.submit_attestation(provider_id, sample_attestation_create_data)

        mock_repository.create.assert_not_called()

    def test_submit_attestation_raises_error_when_not_machine_owner(self, compliance_service, mock_machines_public, sample_attestation_create_data, sample_machine, mock_repository):
        """Test attestation submission fails when provider doesn't own machine"""
        other_provider_id = uuid4()
        provider_id = uuid4()
        sample_machine.provider_id = provider_id
        mock_machines_public.get_machine.return_value = sample_machine

        with pytest.raises(ValueError, match="You do not own this machine"):
            compliance_service.submit_attestation(other_provider_id, sample_attestation_create_data)

        mock_repository.create.assert_not_called()

    def test_submit_attestation_raises_error_when_attestation_already_exists(self, compliance_service, mock_repository, mock_machines_public, sample_attestation_create_data, sample_machine, sample_attestation):
        """Test attestation submission fails when attestation already exists for booking"""
        provider_id = uuid4()
        sample_machine.provider_id = provider_id
        mock_machines_public.get_machine.return_value = sample_machine
        mock_repository.get_by_booking.return_value = sample_attestation

        with pytest.raises(ValueError, match="Wipe attestation already exists for this booking"):
            compliance_service.submit_attestation(provider_id, sample_attestation_create_data)

        mock_repository.create.assert_not_called()

    def test_admin_review_successfully_updates_attestation(self, compliance_service, mock_db, mock_repository, sample_attestation, sample_attestation_update_data):
        """Test successful admin review and status update"""
        attestation_id = uuid4()
        mock_repository.update_status.return_value = sample_attestation
        
        result = compliance_service.admin_review(attestation_id, sample_attestation_update_data)

        mock_repository.update_status.assert_called_once_with(
            mock_db, 
            attestation_id, 
            sample_attestation_update_data.status
        )
        assert result == sample_attestation

    def test_admin_review_raises_error_when_attestation_not_found(self, compliance_service, mock_repository, sample_attestation_update_data):
        """Test admin review raises error when attestation doesn't exist"""
        attestation_id = uuid4()
        mock_repository.update_status.return_value = None

        with pytest.raises(ValueError, match="Attestation not found"):
            compliance_service.admin_review(attestation_id, sample_attestation_update_data)

    def test_get_attestation_by_booking_delegates_to_repository(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation):
        """Test getting attestation by booking delegates to repository"""
        mock_repository.get_by_booking.return_value = sample_attestation

        result = compliance_service.get_attestation_by_booking(sample_booking)

        mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)
        assert result == sample_attestation

    def test_get_attestation_by_booking_returns_none_when_not_found(self, compliance_service, mock_db, mock_repository, sample_booking):
        """Test getting attestation by booking returns None when not found"""
        mock_repository.get_by_booking.return_value = None

        result = compliance_service.get_attestation_by_booking(sample_booking)

        assert result is None
        mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)

    def test_list_machine_attestations_delegates_to_repository(self, compliance_service, mock_db, mock_repository):
        """Test listing machine attestations delegates to repository"""
        machine_id = uuid4()
        sample_attestations = [Mock(spec=WipeAttestation), Mock(spec=WipeAttestation)]
        mock_repository.list_machine_attestations.return_value = sample_attestations

        result = compliance_service.list_machine_attestations(machine_id)

        mock_repository.list_machine_attestations.assert_called_once_with(mock_db, machine_id)
        assert result == sample_attestations

    def test_list_machine_attestations_returns_empty_list_when_none_exist(self, compliance_service, mock_db, mock_repository):
        """Test listing machine attestations returns empty list when none exist"""
        machine_id = uuid4()
        mock_repository.list_machine_attestations.return_value = []

        result = compliance_service.list_machine_attestations(machine_id)

        mock_repository.list_machine_attestations.assert_called_once_with(mock_db, machine_id)
        assert result == []

    def test_list_all_attestations_delegates_to_repository(self, compliance_service, mock_db, mock_repository):
        """Test listing all attestations delegates to repository"""
        sample_attestations = [Mock(spec=WipeAttestation), Mock(spec=WipeAttestation)]
        mock_repository.list_all.return_value = sample_attestations

        result = compliance_service.list_all_attestations()

        mock_repository.list_all.assert_called_once_with(mock_db)
        assert result == sample_attestations

    def test_list_all_attestations_returns_empty_list_when_none_exist(self, compliance_service, mock_db, mock_repository):
        """Test listing all attestations returns empty list when none exist"""
        mock_repository.list_all.return_value = []

        result = compliance_service.list_all_attestations()

        mock_repository.list_all.assert_called_once_with(mock_db)
        assert result == []

    def test_get_buyer_verification_returns_verification(self, compliance_service, mock_db, mock_repository, sample_attestation_with_relations):
        """Test buyer verification returns public verification data"""
        booking_id = uuid4()
        user_id = sample_attestation_with_relations.booking.buyer_user_id
        mock_repository.get_by_booking_with_relations.return_value = sample_attestation_with_relations

        result = compliance_service.get_buyer_verification(booking_id, user_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)
        assert isinstance(result, WipeVerificationPublic)

    def test_get_buyer_verification_raises_error_when_no_attestation(self, compliance_service, mock_db, mock_repository):
        """Test buyer verification raises error when no attestation exists"""
        booking_id = uuid4()
        user_id = uuid4()
        mock_repository.get_by_booking_with_relations.return_value = None

        with pytest.raises(ValueError, match="No booking attestation found."):
            compliance_service.get_buyer_verification(booking_id, user_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)

    def test_get_buyer_verification_raises_error_when_not_booking_owner(self, compliance_service, mock_db, mock_repository, sample_attestation_with_relations):
        """Test buyer verification raises error when user doesn't own booking"""
        booking_id = uuid4()
        different_user_id = uuid4()
        mock_repository.get_by_booking_with_relations.return_value = sample_attestation_with_relations

        with pytest.raises(ValueError, match="Not your booking"):
            compliance_service.get_buyer_verification(booking_id, different_user_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)

    def test_get_provider_attestation_returns_full_attestation(self, compliance_service, mock_db, mock_repository, sample_attestation_with_relations):
        """Test provider attestation returns full attestation for their machine"""
        booking_id = uuid4()
        provider_id = sample_attestation_with_relations.machine.provider_id
        mock_repository.get_by_booking_with_relations.return_value = sample_attestation_with_relations

        result = compliance_service.get_provider_attestation(provider_id, booking_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)
        assert result == sample_attestation_with_relations

    def test_get_provider_attestation_raises_error_when_no_attestation(self, compliance_service, mock_db, mock_repository):
        """Test provider attestation raises error when no attestation exists"""
        booking_id = uuid4()
        provider_id = uuid4()
        mock_repository.get_by_booking_with_relations.return_value = None

        with pytest.raises(ValueError, match="No wipe attestation found"):
            compliance_service.get_provider_attestation(provider_id, booking_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)

    def test_get_provider_attestation_raises_error_when_not_machine_owner(self, compliance_service, mock_db, mock_repository, sample_attestation_with_relations):
        """Test provider attestation raises error when provider doesn't own machine"""
        booking_id = uuid4()
        different_provider_id = uuid4()
        mock_repository.get_by_booking_with_relations.return_value = sample_attestation_with_relations

        with pytest.raises(ValueError, match="Not authorized"):
            compliance_service.get_provider_attestation(different_provider_id, booking_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)

    def test_get_admin_attestation_returns_full_attestation(self, compliance_service, mock_db, mock_repository, sample_attestation_with_relations):
        """Test admin attestation returns full attestation"""
        booking_id = uuid4()
        mock_repository.get_by_booking_with_relations.return_value = sample_attestation_with_relations

        result = compliance_service.get_admin_attestation(booking_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)
        assert result == sample_attestation_with_relations

    def test_get_admin_attestation_raises_error_when_no_attestation(self, compliance_service, mock_db, mock_repository):
        """Test admin attestation raises error when no attestation exists"""
        booking_id = uuid4()
        mock_repository.get_by_booking_with_relations.return_value = None

        with pytest.raises(ValueError, match="No wipe attestation found"):
            compliance_service.get_admin_attestation(booking_id)

        mock_repository.get_by_booking_with_relations.assert_called_once_with(mock_db, booking_id)