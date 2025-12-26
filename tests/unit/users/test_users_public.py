import pytest
from unittest.mock import Mock, create_autospec, patch

from app.users.models import User, UserRole
from app.users.public import UsersPublicImpl, get_users_public


def test_users_public_implements_protocol():
    """Test that UsersPublicImpl properly implements the UsersPublic protocol"""
    # Verify all protocol methods exist and are callable
    mock_db = Mock()
    public_impl = UsersPublicImpl(mock_db)
    
    # Verify all protocol methods exist and are callable
    assert hasattr(public_impl, 'get_user_by_supabase_id')
    assert hasattr(public_impl, 'get_user')
    assert hasattr(public_impl, 'get_role')
    assert hasattr(public_impl, 'create_user')
    assert hasattr(public_impl, 'get_or_create_user_by_supabase_id')
    assert hasattr(public_impl, 'is_buyer_role')
    assert hasattr(public_impl, 'is_provider_role')
    assert hasattr(public_impl, 'is_admin_role')
    
    # Verify they're callable
    assert callable(public_impl.get_user_by_supabase_id)
    assert callable(public_impl.get_user)
    assert callable(public_impl.get_role)
    assert callable(public_impl.create_user)
    assert callable(public_impl.get_or_create_user_by_supabase_id)
    assert callable(public_impl.is_buyer_role)
    assert callable(public_impl.is_provider_role)
    assert callable(public_impl.is_admin_role)

def test_role_checking_methods_work_correctly():
    """Test the business logic for role-based permissions"""
    # Test is_buyer_role, is_provider_role, is_admin_role with different user roles

    mock_db = Mock()
    public_impl = UsersPublicImpl(mock_db)
    
    # Mock users with different roles
    buyer_user = Mock(spec=User, role=UserRole.BUYER)
    provider_user = Mock(spec=User, role=UserRole.PROVIDER)  
    admin_user = Mock(spec=User, role=UserRole.ADMIN)
    
    # Test each role checker
    assert public_impl.is_buyer_role(buyer_user) == True
    assert public_impl.is_buyer_role(provider_user) == False
    assert public_impl.is_buyer_role(admin_user) == False
    
    assert public_impl.is_provider_role(buyer_user) == False
    assert public_impl.is_provider_role(provider_user) == True
    assert public_impl.is_provider_role(admin_user) == False
    
    assert public_impl.is_admin_role(buyer_user) == False  
    assert public_impl.is_admin_role(provider_user) == False
    assert public_impl.is_admin_role(admin_user) == True

def test_get_or_create_delegates_to_repository():
    """Test the integration between public interface and repository"""
    # Verify it calls the repository with correct parameters
    mock_db = Mock()
    public_impl = UsersPublicImpl(mock_db)
    
    # Mock the repository method
    with patch.object(public_impl.repo, 'get_or_create_user_by_supabase_id') as mock_repo_method:
        mock_user = Mock()
        mock_repo_method.return_value = mock_user
        
        # Call the public interface
        result = public_impl.get_or_create_user_by_supabase_id("auth|123", "test@example.com", UserRole.BUYER)
        
        # Verify it delegates to repository with correct parameters
        mock_repo_method.assert_called_once_with(mock_db, sub="auth|123", email="test@example.com", role=UserRole.BUYER)
        assert result == mock_user