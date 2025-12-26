import pytest
from unittest.mock import Mock, patch
from jwt import PyJWTError
import jwt

from app.auth.service import AuthService
from app.users.models import User, UserRole


class TestAuthService:
    
    def test_init_dependencies_injected(self):
        """Test that AuthService properly receives its dependencies"""
        mock_db = Mock()
        mock_users_public = Mock()
        
        service = AuthService(db=mock_db, users_public=mock_users_public)
        
        assert service.db == mock_db
        assert service.users_public == mock_users_public

    def test_decode_supabase_jwt_success(self):
        """Test successful JWT decoding"""
        mock_db = Mock()
        mock_users_public = Mock()
        service = AuthService(mock_db, mock_users_public)
        service.supabase_jwt_secret = "test_secret"
        
        test_payload = {"sub": "123", "email": "test@example.com"}
        token = jwt.encode(test_payload, "test_secret", algorithm="HS256")
        
        result = service._decode_supabase_jwt(token)
        
        assert result["sub"] == "123"
        assert result["email"] == "test@example.com"

    def test_decode_supabase_jwt_missing_secret_raises_error(self):
        """Test error when JWT secret is not configured"""
        mock_db = Mock()
        mock_users_public = Mock()
        service = AuthService(mock_db, mock_users_public)
        service.supabase_jwt_secret = None
        
        with pytest.raises(RuntimeError, match="SUPABASE_JWT_SECRET not set"):
            service._decode_supabase_jwt("any_token")

    def test_decode_supabase_jwt_invalid_token_raises_error(self):
        """Test error handling for invalid JWT tokens"""
        mock_db = Mock()
        mock_users_public = Mock()
        service = AuthService(mock_db, mock_users_public)
        service.supabase_jwt_secret = "test_secret"
        
        with pytest.raises(ValueError, match="Invalid or expired JWT"):
            service._decode_supabase_jwt("invalid.token.here")

    def test_get_current_user_with_mock_token(self):
        """Test mock token parsing (local dev/test format)"""
        mock_db = Mock()
        mock_users_public = Mock()
        mock_user = Mock(spec=User)
        mock_users_public.get_or_create_user_by_supabase_id.return_value = mock_user
        
        service = AuthService(mock_db, mock_users_public)
        
        #mock token format
        result = service.get_current_user("provider:alice@example.com")

        assert result == mock_user
        mock_users_public.get_or_create_user_by_supabase_id.assert_called_once_with(
            sub="alice@example.com",
            email="alice@example.com", 
            role="provider"
        )

    def test_get_current_user_strips_bearer_prefix(self):
        """Test that Bearer prefix is properly handled"""
        mock_db = Mock()
        mock_users_public = Mock()
        mock_user = Mock(spec=User)
        mock_users_public.get_or_create_user_by_supabase_id.return_value = mock_user
        
        service = AuthService(mock_db, mock_users_public)

        result = service.get_current_user("Bearer provider:alice@example.com")

        assert result == mock_user
        #Should call with stripped token
        mock_users_public.get_or_create_user_by_supabase_id.assert_called_once_with(
            sub="alice@example.com",
            email="alice@example.com",
            role="provider"
        )

    def test_get_current_user_with_supabase_jwt(self):
        """Test real JWT token processing"""
        mock_db = Mock()
        mock_users_public = Mock()
        mock_user = Mock(spec=User)
        mock_users_public.get_or_create_user_by_supabase_id.return_value = mock_user
        
        service = AuthService(mock_db, mock_users_public)
        service.supabase_jwt_secret = "test_secret"
        
        #Create a real JWT token
        jwt_payload = {
            "sub": "auth0|12345",
            "email": "jwt_user@example.com", 
            "user_metadata": {"role": "buyer"}
        }
        token = jwt.encode(jwt_payload, "test_secret", algorithm="HS256")
    
        result = service.get_current_user(token)
        
        assert result == mock_user
        mock_users_public.get_or_create_user_by_supabase_id.assert_called_once_with(
            sub="auth0|12345",
            email="jwt_user@example.com",
            role="buyer"
        )

    def test_get_current_user_returns_none_for_no_token(self):
        """Test that None token returns None user"""
        mock_db = Mock()
        mock_users_public = Mock()
        
        service = AuthService(mock_db, mock_users_public)
        
        result = service.get_current_user(None)
        
        assert result is None
        mock_users_public.get_or_create_user_by_supabase_id.assert_not_called()

    def test_get_current_user_invalid_jwt_payload_raises_error(self):
        """Test error for JWT missing required fields"""
        mock_db = Mock()
        mock_users_public = Mock()
        
        service = AuthService(mock_db, mock_users_public)
        service.supabase_jwt_secret = "test_secret"
        
        # JWT missing email
        jwt_payload = {"sub": "auth0|12345"}  # No email
        token = jwt.encode(jwt_payload, "test_secret", algorithm="HS256")
        
        with pytest.raises(ValueError, match="Invalid JWT payload: missing 'sub' or 'email'"):
            service.get_current_user(token)

    def test_get_or_create_user_delegates_to_users_public(self):
        """Test that user provisioning delegates to Users domain"""
        mock_db = Mock()
        mock_users_public = Mock()
        mock_user = Mock(spec=User)
        mock_users_public.get_or_create_user_by_supabase_id.return_value = mock_user
        
        service = AuthService(mock_db, mock_users_public)
        
        result = service._get_or_create_user("sub123", "test@example.com", "admin")
        
        assert result == mock_user
        mock_users_public.get_or_create_user_by_supabase_id.assert_called_once_with(
            sub="sub123", email="test@example.com", role="admin"
        )

    def test_dependency_injection_works(self):
        """Test FastAPI dependency injection"""
        from app.auth.service import get_auth_service
        
        mock_db = Mock()
        mock_users_public = Mock()
        
        service = get_auth_service(db=mock_db, users_public=mock_users_public)
        
        assert isinstance(service, AuthService)
        assert service.db == mock_db
        assert service.users_public == mock_users_public