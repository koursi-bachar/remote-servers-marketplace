from app.users.public import get_users_public
from app.users.models import UserRole
from test_config import TestConfig


def create_user(db_session, email: str, role: str):
    """Pure factory - creates user with given email and role."""
    users_public = get_users_public(db_session)
    return users_public.create_user(
        email=email,
        supabase_id=email,
        role=getattr(UserRole, role.upper()),
    )

def create_user_by_role(db_session, role="buyer"):
    """Config-aware: Create user with standardized test credentials."""
    email = getattr(TestConfig, f"{role.upper()}_EMAIL")
    return create_user(db_session, email, role)

def create_admin_user(db_session):
    """Convenience function for creating an admin user."""
    return create_user_by_role(db_session, "admin")

def create_provider_user(db_session):
    """Convenience function for creating a provider user."""
    return create_user_by_role(db_session, "provider")

def create_buyer_user(db_session):
    """Convenience function for creating a buyer user."""
    return create_user_by_role(db_session, "buyer")

def auth_headers_for(email: str, role: str):
    """Pure factory - creates auth headers for given email and role."""
    return {"Authorization": f"Bearer {role}:{email}"}

def auth_headers_by_role(role):
    """Config-aware: Get auth headers for standardized test roles."""
    email = getattr(TestConfig, f"{role.upper()}_EMAIL")
    return auth_headers_for(email, role)