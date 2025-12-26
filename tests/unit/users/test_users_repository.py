import pytest
from unittest.mock import Mock, create_autospec, patch
from sqlalchemy.orm import Session

from app.users.repository import UsersRepository
from app.users.models import User, UserRole


class TestUsersRepository:

    def test_get_user_by_supabase_id_returns_user_when_exists(self):
        mock_db = Mock()
        mock_user = Mock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        result = UsersRepository().get_user_by_supabase_id(mock_db, "test_id")
        
        assert result == mock_user

    def test_get_user_by_supabase_id_returns_none_when_not_found(self):  
        mock_db = Mock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        result = UsersRepository().get_user_by_supabase_id(mock_db, "nonexistent_id")
        
        assert result is None

    def test_create_user_successfully_creates_user(self):
        mock_db = Mock()
        repository = UsersRepository()
        
        result = repository.create_user(
            mock_db, "test@example.com", "auth|123", UserRole.BUYER
        )
        
        assert mock_db.add.called
        assert mock_db.commit.called  
        assert result is not None

    def test_create_user_auto_generates_supabase_id_when_none(self):
        mock_db = Mock()
        repository = UsersRepository()
        
        result = repository.create_user(
            mock_db, "test@example.com", None, UserRole.BUYER
        )

        assert mock_db.add.called
        assert mock_db.commit.called  
        assert result is not None

    def test_get_or_create_returns_existing_user_when_found(self):
        """
        Test that when a user already exists with the given supabase_id,
        the method returns the existing user instead of creating a new one.
        """
        mock_db = Mock()
        repository = UsersRepository()
        
        mock_existing_user = Mock(spec=User)
        
        with patch.object(repository, 'get_user_by_supabase_id') as mock_get_user:
            with patch.object(repository, 'create_user') as mock_create_user:
                mock_get_user.return_value = mock_existing_user
                
                result = repository.get_or_create_user_by_supabase_id(
                    mock_db, "auth|123", "test@example.com", "buyer"
                )
                
                assert result == mock_existing_user
                mock_get_user.assert_called_once_with(mock_db, "auth|123")
                mock_create_user.assert_not_called()

    def test_get_or_create_creates_new_user_when_not_found(self):
        """
        Test that when no user exists with the given supabase_id,
        the method creates a new user with the correct role conversion.
        """
        mock_db = Mock()
        repository = UsersRepository()

        with patch.object(repository, 'get_user_by_supabase_id') as mock_get_user:
            with patch.object(repository, 'create_user') as mock_create_user:
                mock_get_user.return_value = None

                mock_new_user = Mock()
                mock_create_user.return_value = mock_new_user
                
                result = repository.get_or_create_user_by_supabase_id(
                    mock_db, "auth|123", "test@example.com", "buyer"
                )

                assert result == mock_new_user
                mock_get_user.assert_called_once_with(mock_db, "auth|123")
                
                mock_create_user.assert_called_once_with(
                    mock_db,
                    email="test@example.com",
                    supabase_id="auth|123",
                    role=UserRole.BUYER  #Tests the string -> enum conversion
                )