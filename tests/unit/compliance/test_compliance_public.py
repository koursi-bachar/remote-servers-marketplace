import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.compliance.public import CompliancePublicImpl


def test_compliance_public_implements_protocol():
    """Test that CompliancePublicImpl properly implements the CompliancePublic protocol"""
    mock_service = Mock()
    public_impl = CompliancePublicImpl(mock_service)
    
    assert hasattr(public_impl, 'simulate_wipe_for_booking')
    assert hasattr(public_impl, 'get_attestation_by_booking')
    assert hasattr(public_impl, 'require_attestation_for_booking')
    
    assert callable(public_impl.simulate_wipe_for_booking)
    assert callable(public_impl.get_attestation_by_booking)
    assert callable(public_impl.require_attestation_for_booking)

def test_compliance_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    public_impl = CompliancePublicImpl(mock_service)
    
    mock_booking = Mock()
    mock_booking.id = uuid4()
    mock_attestation = Mock()
    
    mock_service.simulate_wipe_for_booking.return_value = mock_attestation
    result = public_impl.simulate_wipe_for_booking(mock_booking)
    assert result == mock_attestation
    mock_service.simulate_wipe_for_booking.assert_called_once_with(mock_booking)
    
    mock_service.reset_mock()
    
    mock_service.get_attestation_by_booking.return_value = mock_attestation
    result = public_impl.get_attestation_by_booking(mock_booking)
    assert result == mock_attestation
    mock_service.get_attestation_by_booking.assert_called_once_with(mock_booking)
    
    mock_service.reset_mock()
    
    mock_service.require_attestation_for_booking.return_value = mock_attestation
    result = public_impl.require_attestation_for_booking(mock_booking)
    assert result == mock_attestation
    mock_service.require_attestation_for_booking.assert_called_once_with(mock_booking)