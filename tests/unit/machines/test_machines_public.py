import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.machines.public import MachinesPublicImpl


def test_machines_public_implements_protocol():
    """Test that MachinesPublicImpl properly implements the MachinesPublic protocol"""
    #Verify all protocol methods exist and are callable
    mock_service = Mock()
    public_impl = MachinesPublicImpl(mock_service)
    
    #Verify all protocol methods exist and are callable
    assert hasattr(public_impl, 'provider_owns_machine')
    assert hasattr(public_impl, 'get_machine')
    assert hasattr(public_impl, 'list_machines_for_provider')
    
    #Verify they're callable
    assert callable(public_impl.provider_owns_machine)
    assert callable(public_impl.get_machine)
    assert callable(public_impl.list_machines_for_provider)

def test_ownership_checking_logic_works_correctly():
    """Test the business logic for machine ownership checking"""
    #Test provider_owns_machine with different scenarios
    
    mock_service = Mock()
    public_impl = MachinesPublicImpl(mock_service)
    
    #Create test IDs
    owner_id = uuid4()
    different_owner_id = uuid4()
    machine_id = uuid4()
    
    #Mock machine owned by owner_id
    mock_owned_machine = Mock()
    mock_owned_machine.provider_id = owner_id
    
    #Mock machine owned by different owner
    mock_other_machine = Mock()
    mock_other_machine.provider_id = different_owner_id
    
    #Test 1: Owner checks their own machine
    mock_service.get_machine.return_value = mock_owned_machine
    assert public_impl.provider_owns_machine(owner_id, machine_id) == True
    
    #Test 2: Different owner checks someone else's machine
    mock_service.get_machine.return_value = mock_owned_machine
    assert public_impl.provider_owns_machine(different_owner_id, machine_id) == False
    
    #Test 3: Machine doesn't exist
    mock_service.get_machine.side_effect = ValueError("Machine does not exist")
    assert public_impl.provider_owns_machine(owner_id, machine_id) == False