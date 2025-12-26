import pytest
from unittest.mock import Mock, patch

from app.auth.auth import extract_token, get_current_user, optional_user, require_roles


class TestAuthDependencies:
    
    def test_extract_token_from_header(self):
        """Test token extraction from Authorization header"""
        mock_credentials = Mock()
        mock_credentials.credentials = "header_token"
        mock_request = Mock()
        mock_request.cookies.get.return_value = "cookie_token"
        
        result = extract_token(mock_credentials, mock_request)
        
        assert result == "header_token"  # Header takes priority

    def test_extract_token_from_cookie(self):
        """Test token extraction from cookies when no header"""
        mock_credentials = Mock()
        mock_credentials.credentials = None  # No header token
        mock_request = Mock()
        mock_request.cookies.get.return_value = "cookie_token"
        
        result = extract_token(mock_credentials, mock_request)
        
        assert result == "cookie_token"

    def test_extract_token_returns_none_when_no_tokens(self):
        """Test token extraction returns None when no tokens available"""
        mock_credentials = Mock()
        mock_credentials.credentials = None
        mock_request = Mock()
        mock_request.cookies.get.return_value = None
        
        result = extract_token(mock_credentials, mock_request)
        
        assert result is None

    def test_get_current_user_success(self):
        """Test successful user authentication"""
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "valid_token"
        mock_auth_service = Mock()
        mock_user = Mock()
        
        mock_auth_service.get_current_user.return_value = mock_user
        
        # Use patch to mock the dependencies
        with patch('app.auth.auth.get_auth_service') as mock_get_auth_service:
            mock_get_auth_service.return_value = mock_auth_service
            
            result = get_current_user(mock_request, mock_credentials, mock_auth_service)
            
            assert result == mock_user
            mock_auth_service.get_current_user.assert_called_once_with("valid_token")

    def test_get_current_user_auth_service_error(self):
        """Test error handling when auth service fails"""
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid_token"
        mock_auth_service = Mock()
        
        mock_auth_service.get_current_user.side_effect = Exception("Auth failed")
        
        with patch('app.auth.auth.get_auth_service') as mock_get_auth_service:
            mock_get_auth_service.return_value = mock_auth_service
            
            with pytest.raises(Exception) as exc_info:
                get_current_user(mock_request, mock_credentials, mock_auth_service)
            
            assert "Auth failed" in str(exc_info.value.detail)

    def test_get_current_user_no_user_found(self):
        """Test error when no user found for token"""
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "valid_but_unknown_token"
        mock_auth_service = Mock()
        
        mock_auth_service.get_current_user.return_value = None
        
        with patch('app.auth.auth.get_auth_service') as mock_get_auth_service:
            mock_get_auth_service.return_value = mock_auth_service
            
            with pytest.raises(Exception) as exc_info:
                get_current_user(mock_request, mock_credentials, mock_auth_service)
            
            assert "Invalid or missing authentication token" in str(exc_info.value.detail)

    def test_optional_user_returns_user_when_authenticated(self):
        """Test optional_user returns user when authentication succeeds"""
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "valid_token"
        mock_auth_service = Mock()
        mock_user = Mock()
        
        mock_auth_service.get_current_user.return_value = mock_user
        
        with patch('app.auth.auth.get_auth_service') as mock_get_auth_service:
            mock_get_auth_service.return_value = mock_auth_service
            
            result = optional_user(mock_request, mock_credentials, mock_auth_service)
            
            assert result == mock_user

    def test_optional_user_returns_none_when_auth_fails(self):
        """Test optional_user returns None when authentication fails"""
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid_token"
        mock_auth_service = Mock()
        
        mock_auth_service.get_current_user.side_effect = Exception("Auth failed")
        
        with patch('app.auth.auth.get_auth_service') as mock_get_auth_service:
            mock_get_auth_service.return_value = mock_auth_service
            
            result = optional_user(mock_request, mock_credentials, mock_auth_service)
            
            assert result is None

    def test_require_roles_decorator_with_valid_role(self):
        """Test require_roles allows access with valid role"""
        mock_user = Mock()
        mock_user.role = "admin"
        
        # Create the dependency
        role_dependency = require_roles("admin", "provider")
        
        # The dependency should return the user when role matches
        result = role_dependency(user=mock_user)
        
        assert result == mock_user

    def test_require_roles_decorator_with_invalid_role(self):
        """Test require_roles denies access with invalid role"""
        mock_user = Mock()
        mock_user.role = "buyer"  # Not in allowed roles
        
        role_dependency = require_roles("admin", "provider")
        
        with pytest.raises(Exception) as exc_info:
            role_dependency(user=mock_user)
        
        assert "Not enough permissions" in str(exc_info.value.detail)