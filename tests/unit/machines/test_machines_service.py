import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.machines.service import MachinesService
from app.machines.repository import MachinesRepository
from app.machines.models import Machine
from app.machines.schemas import MachineCreate


@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_repository():
    return Mock(spec=MachinesRepository)

@pytest.fixture
def machines_service(mock_db, mock_repository):
    """Main service fixture that composes other fixtures"""
    return MachinesService(
        db=mock_db,
        machine_repo=mock_repository,
        providers_public=Mock(),
    )

@pytest.fixture
def sample_machine_data():
    """Fixture for sample machine creation data"""
    return MachineCreate(
        provider_id=uuid4(),
        hostname="test-machine",
        location_region="us-west",
        gpu_model="RTX 4090",
        gpu_count=1,
        vram_gb=24,
        cpu_model="Intel i9",
        cpu_cores=8,
        ram_gb=16,
        storage_gb=500,
        network_mbps=1000,
        notes="Test machine"
    )

class TestMachinesService:

    def test_get_machine_returns_machine_when_exists(self, machines_service, mock_db, mock_repository):
        """Test successful machine retrieval"""
        mock_existing_machine = Mock(spec=Machine)
        machine_id = uuid4()
        
        mock_repository.get_machine.return_value = mock_existing_machine
        
        result = machines_service.get_machine(machine_id)
        
        assert result == mock_existing_machine
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)

    def test_get_machine_raises_error_when_not_found(self, machines_service, mock_db, mock_repository):
        """Test error when machine doesn't exist"""
        machine_id = uuid4()

        mock_repository.get_machine.return_value = None

        with pytest.raises(ValueError, match="Machine does not exist."):
            machines_service.get_machine(machine_id)
        
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)

    def test_list_machines_for_provider_delegates_to_repository(self, machines_service, mock_db, mock_repository):
        """Test listing machines delegates to repository"""
        mock_machines = [Mock(spec=Machine), Mock(spec=Machine)]
        provider_id = uuid4()

        mock_repository.list_machines_for_provider.return_value = mock_machines

        result = machines_service.list_machines_for_provider(provider_id)

        assert result == mock_machines
        mock_repository.list_machines_for_provider.assert_called_once_with(mock_db, provider_id)

    def test_create_machine_delegates_to_repository(self, machines_service, mock_db, mock_repository, sample_machine_data):
        """Test machine creation delegates to repository"""
        mock_machine = Mock(spec=Machine)
        
        mock_repository.create_machine.return_value = mock_machine
        
        result = machines_service.create_machine(sample_machine_data)
        
        assert result == mock_machine
        mock_repository.create_machine.assert_called_once_with(mock_db, sample_machine_data)

    def test_delete_machine_successfully_deletes_owned_machine(self, machines_service, mock_db, mock_repository):
        """Test successful deletion when provider owns machine"""
        owner_id = uuid4()
        machine_id = uuid4()
        mock_machine = Mock(spec=Machine)
        mock_machine.provider_id = owner_id

        mock_repository.get_machine.return_value = mock_machine

        machines_service.delete_machine(machine_id, owner_id)

        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)
        mock_repository.delete_machine.assert_called_once_with(mock_db, mock_machine)

    def test_delete_machine_raises_error_when_machine_not_found(self, machines_service, mock_db, mock_repository):
        """Test error when deleting non-existent machine"""
        machine_id = uuid4()
        provider_id = uuid4()

        mock_repository.get_machine.return_value = None

        with pytest.raises(ValueError, match="Machine does not exist."):
            machines_service.delete_machine(machine_id, provider_id)
        
        mock_repository.delete_machine.assert_not_called()

    def test_delete_machine_raises_error_when_not_owner(self, machines_service, mock_db, mock_repository):
        """Test error when provider doesn't own machine"""
        owner_a_id = uuid4()
        owner_b_id = uuid4()
        machine_id = uuid4()
        
        mock_machine = Mock(spec=Machine)
        mock_machine.provider_id = owner_a_id
        
        mock_repository.get_machine.return_value = mock_machine

        with pytest.raises(ValueError, match="You do not own this machine"):
                machines_service.delete_machine(machine_id, owner_b_id)
        
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)
        mock_repository.delete_machine.assert_not_called()