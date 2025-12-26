import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.organizations.public import OrganizationsPublicImpl


def test_organizations_public_implements_protocol():
    """Test that OrganizationsPublicImpl properly implements the OrganizationsPublic protocol"""
    mock_service = Mock()
    public_impl = OrganizationsPublicImpl(mock_service)
    
    assert hasattr(public_impl, 'get_organization')
    assert hasattr(public_impl, 'is_org_admin')
    assert hasattr(public_impl, 'is_org_member')
    assert hasattr(public_impl, 'list_user_organizations')
    assert hasattr(public_impl, 'get_membership')
    
    assert callable(public_impl.get_organization)
    assert callable(public_impl.is_org_admin)
    assert callable(public_impl.is_org_member)
    assert callable(public_impl.list_user_organizations)
    assert callable(public_impl.get_membership)

def test_organizations_public_delegates_to_service():
    """Test that all public methods correctly delegate to the service layer"""
    mock_service = Mock()
    public_impl = OrganizationsPublicImpl(mock_service)
    
    org_id = uuid4()
    user_id = uuid4()
    mock_organization = Mock()
    mock_organizations_list = [Mock(), Mock()]
    mock_membership = Mock()
    
    mock_service.repo.get.return_value = mock_organization
    result = public_impl.get_organization(org_id)
    assert result == mock_organization
    mock_service.repo.get.assert_called_once_with(org_id)
    
    mock_service.repo.reset_mock()
    
    mock_service.is_org_admin.return_value = True
    result = public_impl.is_org_admin(user_id, org_id)
    assert result == True
    mock_service.is_org_admin.assert_called_once_with(user_id, org_id)
    
    mock_service.reset_mock()
    
    mock_service.is_org_member.return_value = True
    result = public_impl.is_org_member(user_id, org_id)
    assert result == True
    mock_service.is_org_member.assert_called_once_with(user_id, org_id)
    
    mock_service.reset_mock()
    
    mock_service.list_user_organizations.return_value = mock_organizations_list
    result = public_impl.list_user_organizations(user_id)
    assert result == mock_organizations_list
    mock_service.list_user_organizations.assert_called_once_with(user_id)
    
    mock_service.repo.reset_mock()
    
    mock_service.repo.get_membership.return_value = mock_membership
    result = public_impl.get_membership(org_id, user_id)
    assert result == mock_membership
    mock_service.repo.get_membership.assert_called_once_with(org_id, user_id)