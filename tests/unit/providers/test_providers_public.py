import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.providers.public import ProvidersPublicImpl
from app.providers.models import ProviderVerificationStatus


def test_providers_public_implements_protocol():
    """Test that ProvidersPublicImpl properly implements the ProvidersPublic protocol"""
    mock_profile_service = Mock()
    mock_verification_service = Mock()
    public_impl = ProvidersPublicImpl(mock_profile_service, mock_verification_service)
    
    assert hasattr(public_impl, 'get_profile_by_user')
    assert hasattr(public_impl, 'require_verified_provider')
    assert hasattr(public_impl, 'is_verified')
    assert hasattr(public_impl, 'list_verifications')
    
    assert callable(public_impl.get_profile_by_user)
    assert callable(public_impl.require_verified_provider)
    assert callable(public_impl.is_verified)
    assert callable(public_impl.list_verifications)

def test_providers_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_profile_service = Mock()
    mock_verification_service = Mock()
    public_impl = ProvidersPublicImpl(mock_profile_service, mock_verification_service)
    
    user_id = uuid4()
    mock_profile = Mock()
    mock_verified_profile = Mock()
    mock_verifications_result = [Mock(), Mock()]
    
    mock_profile_service.repo.get_by_user_id.return_value = mock_profile
    result = public_impl.get_profile_by_user(user_id)
    assert result == mock_profile
    mock_profile_service.repo.get_by_user_id.assert_called_once_with(user_id)
    
    mock_profile_service.reset_mock()
    mock_verification_service.reset_mock()
    
    mock_profile_service.require_verified.return_value = mock_verified_profile
    result = public_impl.require_verified_provider(user_id)
    assert result == mock_verified_profile
    mock_profile_service.require_verified.assert_called_once_with(user_id)
    
    mock_profile_service.reset_mock()
    mock_verification_service.reset_mock()
    
    mock_profile_service.repo.get_by_user_id.return_value = mock_profile
    mock_profile.verification_status = ProviderVerificationStatus.VERIFIED
    result = public_impl.is_verified(user_id)
    assert result == True
    mock_profile_service.repo.get_by_user_id.assert_called_once_with(user_id)
    
    mock_profile_service.reset_mock()
    mock_verification_service.reset_mock()
    
    mock_profile_service.repo.get_by_user_id.return_value = mock_profile
    mock_profile.verification_status = ProviderVerificationStatus.PENDING
    result = public_impl.is_verified(user_id)
    assert result == False
    
    mock_profile_service.reset_mock()
    mock_verification_service.reset_mock()
    
    mock_profile_service.repo.get_by_user_id.return_value = None
    result = public_impl.is_verified(user_id)
    assert result == False
    
    mock_profile_service.reset_mock()
    mock_verification_service.reset_mock()
    
    subject_type = "provider"
    subject_id = uuid4()
    mock_verification_service.list_verifications.return_value = mock_verifications_result
    result = public_impl.list_verifications(subject_type, subject_id)
    assert result == mock_verifications_result
    mock_verification_service.list_verifications.assert_called_once_with(subject_type, subject_id)