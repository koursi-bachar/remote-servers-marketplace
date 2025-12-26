from fastapi import Depends, HTTPException, status
from typing import Protocol

from app.users.public import UsersPublic, get_users_public
from app.auth.auth import get_current_user


class AuthPublic(Protocol):
    
    """Public interface for authentication and authorization checks."""
    def ensure_buyer(self) -> None:
        ...

    def ensure_provider(self) -> None:
        ...

    def ensure_admin(self) -> None:
        ...

class AuthPublicImpl:
    """This delegates role checks to UsersPublic."""
    def __init__(self, current_user, users_public: UsersPublic):
        self.current_user = current_user
        self.users_public = users_public

    def ensure_buyer(self) -> None:
        if not self.users_public.is_buyer_role(self.current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Buyer role required.",
            )

    def ensure_provider(self) -> None:
        if not self.users_public.is_provider_role(self.current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provider role required.",
            )
        
    def ensure_admin(self) -> None:
        if not self.users_public.is_admin_role(self.current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required.",
            )

def get_auth_public(
    current_user = Depends(get_current_user),
    users_public: UsersPublic = Depends(get_users_public),
) -> AuthPublic:
    """
    Dependency injection provider for AuthPublic interface.
    """
    return AuthPublicImpl(current_user=current_user, users_public=users_public)

"""Direct FastAPI dependencies for common use cases"""

def ensure_buyer(auth_public: AuthPublic = Depends(get_auth_public)):
    """FastAPI dependency that ensures current user is a buyer"""
    auth_public.ensure_buyer()
    return auth_public.current_user

def ensure_provider(auth_public: AuthPublic = Depends(get_auth_public)):
    """FastAPI dependency that ensures current user is a provider"""
    auth_public.ensure_provider()
    return auth_public.current_user

def ensure_admin(auth_public: AuthPublic = Depends(get_auth_public)):
    """FastAPI dependency that ensures current user is an admin"""
    auth_public.ensure_admin()
    return auth_public.current_user