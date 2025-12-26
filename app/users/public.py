from typing import Protocol
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from .repository import UsersRepository
from .models import User, UserRole


class UsersPublic(Protocol):
    """Protocol defining the public interface for users queries."""
    def get_user_by_supabase_id(self, sub: str) -> User | None:
        ...

    def get_user(self, user_id: UUID) -> User | None:
        ...

    def get_role(self, user: User) -> UserRole:
        ...

    def create_user(self, email: str, supabase_id: str | None, role: UserRole) -> User:
        ...

    def get_or_create_user_by_supabase_id(self, sub: str, email: str, role: UserRole) -> User:
        ...

    def is_buyer_role(self, user: User) -> bool:
        ...
    
    def is_provider_role(self, user: User) -> bool:
        ...

    def is_admin_role(self, user: User) -> bool:
        ...

class UsersPublicImpl:
    """Concrete implementation of UsersPublic using the UsersRepository."""
    def __init__(self, db: Session):
        self.db = db
        self.repo = UsersRepository()

    def get_user_by_supabase_id(self, sub: str) -> User | None:
        return self.repo.get_user_by_supabase_id(self.db, sub)

    def get_user(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_role(self, user: User) -> UserRole:
        return user.role

    def create_user(self, email: str, supabase_id: str | None, role: UserRole) -> User:
        return self.repo.create_user(self.db, email=email, supabase_id=supabase_id, role=role)

    def get_or_create_user_by_supabase_id(self, sub: str, email: str, role: UserRole) -> User:
        return self.repo.get_or_create_user_by_supabase_id(self.db, sub=sub, email=email, role=role)
    
    def is_buyer_role(self, user: User) -> bool:
        return user.role == UserRole.BUYER
    
    def is_provider_role(self, user: User) -> bool:
        return user.role == UserRole.PROVIDER
    
    def is_admin_role(self, user: User) -> bool:
        return user.role == UserRole.ADMIN


def get_users_public(
    db: Session = Depends(get_db),
) -> UsersPublic:
    """
    FastAPI DI provider for UsersPublic.
    """
    return UsersPublicImpl(db)