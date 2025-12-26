import pytest
from unittest.mock import Mock, create_autospec
from uuid import uuid4
from sqlalchemy.orm import Session

from app.machines.repository import MachinesRepository
from app.machines.models import Machine
from app.machines.schemas import MachineCreate


def create_test_machine_data(**overrides):
        base = {
            "provider_id": uuid4(),
            "hostname": "test-machine",
            "location_region": "us-west",
            "gpu_model": "RTX 4090",
            "gpu_count": 1,
            "vram_gb": 24,
            "cpu_model": "Intel i9",
            "cpu_cores": 8,
            "ram_gb": 16,
            "storage_gb": 500,
            "network_mbps": 1000,
            "notes": "Test machine"
        }
        base.update(overrides)
        return MachineCreate(**base)

class TestMachinesRepository:

    def test_create_machine_successfully_creates_machine(self):
        """Test that machine creation works with valid data"""
        mock_db = Mock()
        repository = MachinesRepository()

        test_data = create_test_machine_data()

        result = repository.create_machine(mock_db, test_data)

        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
        assert result is not None

    def test_get_machine_returns_machine_when_exists(self):
        """Test retrieving an existing machine by ID"""
        mock_db = Mock()
        mock_machine = Mock()
        repository = MachinesRepository()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_machine

        result = repository.get_machine(mock_db, uuid4())

        assert result == mock_machine

    def test_get_machine_returns_none_when_not_found(self):
        """Test retrieving a non-existent machine returns None"""
        mock_db = Mock()
        repository = MachinesRepository()

        mock_db.query.return_value.filter.return_value.first.return_value = None

        provider_id = uuid4()
        result = repository.get_machine(mock_db, provider_id)

        assert result is None

    def test_list_machines_for_provider_returns_provider_machines(self):
        """Test listing machines for a specific provider"""
        mock_db = Mock()
        repository = MachinesRepository()

        mock_machines = [Mock(), Mock()]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_machines
        
        provider_id = uuid4()
        result = repository.list_machines_for_provider(mock_db, provider_id)

        assert result == mock_machines

    def test_list_machines_for_provider_returns_empty_list_when_no_machines(self):
        """Test listing machines returns empty list when provider has none"""
        mock_db = Mock()
        repository = MachinesRepository()

        mock_db.query.return_value.filter.return_value.all.return_value = []

        provider_id = uuid4()
        result = repository.list_machines_for_provider(mock_db, provider_id)

        assert result == []

    def test_provider_owns_machine_returns_true_when_owner(self):
        """Test ownership check returns true when provider owns machine"""
        mock_db = Mock()
        repository = MachinesRepository()

        mock_db.query.return_value.filter.return_value.count.return_value = 1

        provider_id = uuid4()
        machine_id = uuid4()
        result = repository.provider_owns_machine(mock_db, provider_id, machine_id)

        assert result is True

    def test_provider_owns_machine_returns_false_when_not_owner(self):
        """Test ownership check returns false when provider doesn't own machine"""
        mock_db = Mock()
        repository = MachinesRepository()

        mock_db.query.return_value.filter.return_value.count.return_value = 0

        provider_id = uuid4()
        machine_id = uuid4()
        result = repository.provider_owns_machine(mock_db, provider_id, machine_id)

        assert result is False

    def test_delete_machine_performs_database_operations(self):
        """Test that delete_machine calls db.delete and db.commit"""
        mock_db = Mock()
        repository = MachinesRepository()
        mock_machine = Mock()
        
        repository.delete_machine(mock_db, mock_machine)
        
        mock_db.delete.assert_called_once_with(mock_machine)
        mock_db.commit.assert_called_once()