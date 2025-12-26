import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.credentials.public import AccessCredentialsPublicImpl


def test_access_credentials_public_implements_protocol():
    """Test that AccessCredentialsPublicImpl properly implements the AccessCredentialsPublic protocol"""
    mock_service = Mock()
    public_impl = AccessCredentialsPublicImpl(mock_service)
    
    assert hasattr(public_impl, 'issue_for_booking')
    assert hasattr(public_impl, 'revoke_for_booking')
    assert hasattr(public_impl, 'get_for_booking')
    
    assert callable(public_impl.issue_for_booking)
    assert callable(public_impl.revoke_for_booking)
    assert callable(public_impl.get_for_booking)

def test_access_credentials_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    public_impl = AccessCredentialsPublicImpl(mock_service)
    
    mock_booking = Mock()
    mock_booking.id = uuid4()
    mock_credential = Mock()
    mock_credentials_list = [Mock(), Mock()]
    
    mock_service.issue_for_booking.return_value = mock_credential
    result = public_impl.issue_for_booking(mock_booking)
    assert result == mock_credential
    mock_service.issue_for_booking.assert_called_once_with(mock_booking)
    
    mock_service.reset_mock()
    
    mock_service.revoke_for_booking.return_value = mock_credentials_list
    result = public_impl.revoke_for_booking(mock_booking)
    assert result == mock_credentials_list
    mock_service.revoke_for_booking.assert_called_once_with(mock_booking)
    
    mock_service.reset_mock()
    
    mock_service.get_for_booking.return_value = mock_credentials_list
    result = public_impl.get_for_booking(mock_booking)
    assert result == mock_credentials_list
    mock_service.get_for_booking.assert_called_once_with(mock_booking)