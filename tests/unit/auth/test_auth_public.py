import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.auth.public import AuthPublicImpl


class TestAuthPublicImpl:
    
    def test_ensure_buyer_success(self):
        """Test successful buyer role check"""
        mock_current_user = Mock()
        mock_current_user.role = "buyer"
        mock_users_public = Mock()
        mock_users_public.is_buyer_role.return_value = True
        
        auth_public = AuthPublicImpl(mock_current_user, mock_users_public)
        
        #Should not raise exception, no user_id parameter needed
        auth_public.ensure_buyer()
        
        mock_users_public.is_buyer_role.assert_called_once_with(mock_current_user)

    def test_ensure_buyer_fails_for_non_buyer(self):
        """Test buyer check fails for non-buyer role"""
        mock_current_user = Mock()
        mock_current_user.role = "provider"
        mock_users_public = Mock()
        mock_users_public.is_buyer_role.return_value = False
        
        auth_public = AuthPublicImpl(mock_current_user, mock_users_public)
        
        with pytest.raises(Exception) as exc_info:
            auth_public.ensure_buyer()
        
        assert "Buyer role required" in str(exc_info.value.detail)
        mock_users_public.is_buyer_role.assert_called_once_with(mock_current_user)

    @pytest.mark.parametrize("role_method,required_role", [
        ("ensure_provider", "provider"),
        ("ensure_admin", "admin"),
    ])
    def test_role_checks_work_similarly(self, role_method, required_role):
        """Test that all role checks follow the same pattern"""
        mock_current_user = Mock()
        mock_current_user.role = required_role
        mock_users_public = Mock()
        getattr(mock_users_public, f"is_{required_role}_role").return_value = True
        
        auth_public = AuthPublicImpl(mock_current_user, mock_users_public)
        
        #Should not raise exception, no user_id parameter
        getattr(auth_public, role_method)()
        
        getattr(mock_users_public, f"is_{required_role}_role").assert_called_once_with(mock_current_user)

    def test_dependency_injection_returns_implementation(self):
        """Test FastAPI DI for auth public"""
        from app.auth.public import get_auth_public
        
        mock_current_user = Mock()
        mock_users_public = Mock()
        
        #Updated dependency injection test
        result = get_auth_public(current_user=mock_current_user, users_public=mock_users_public)
        
        assert isinstance(result, AuthPublicImpl)
        assert result.current_user == mock_current_user
        assert result.users_public == mock_users_public

    def test_ensure_buyer_dependency(self):
        """Test the ensure_buyer FastAPI dependency"""
        from app.auth.public import ensure_buyer
        
        mock_current_user = Mock()
        mock_auth_public = Mock()
        mock_auth_public.current_user = mock_current_user
        
        result = ensure_buyer(auth_public=mock_auth_public)
        
        assert result == mock_current_user
        mock_auth_public.ensure_buyer.assert_called_once()

    def test_ensure_provider_dependency(self):
        """Test the ensure_provider FastAPI dependency"""
        from app.auth.public import ensure_provider
        
        mock_current_user = Mock()
        mock_auth_public = Mock()
        mock_auth_public.current_user = mock_current_user
        
        result = ensure_provider(auth_public=mock_auth_public)
        
        assert result == mock_current_user
        mock_auth_public.ensure_provider.assert_called_once()

    def test_ensure_admin_dependency(self):
        """Test the ensure_admin FastAPI dependency"""
        from app.auth.public import ensure_admin
        
        mock_current_user = Mock()
        mock_auth_public = Mock()
        mock_auth_public.current_user = mock_current_user
        
        result = ensure_admin(auth_public=mock_auth_public)
        
        assert result == mock_current_user
        mock_auth_public.ensure_admin.assert_called_once()