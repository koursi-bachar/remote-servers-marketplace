import jwt
from jwt import PyJWTError
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.users.public import get_users_public, UsersPublic
from app.users.models import User
from app.config import settings
from app.database import get_db


class AuthService:
    """
    Bridges Supabase authentication with the internal User domain.
    Handles decoding tokens, parsing mock tokens, and provisioning users.
    """
    def __init__(self, db: Session, users_public: UsersPublic):
        self.db = db
        self.supabase_jwt_secret = settings.SUPABASE_JWT_SECRET
        #
        self.users_public = users_public
        #

    def _decode_supabase_jwt(self, token: str) -> dict:
        """
        Decode the JWT we get from Supabase.
        -Uses HS256 with SUPABASE_JWT_SECRET
        -Doesn't verify aud
        """
        if not self.supabase_jwt_secret:
            raise RuntimeError("SUPABASE_JWT_SECRET not set.")

        try:
            return jwt.decode(
                token,
                self.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except PyJWTError as e:
            raise ValueError(f"Invalid or expired JWT: {str(e)}")

    def _get_or_create_user(
        self, sub: str, email: Optional[str], role: Optional[str]
    ) -> User:
        """
        Centralized provision or fetch logic
        """
        return self.users_public.get_or_create_user_by_supabase_id(
            sub=sub,
            email=email,
            role=role,
        )

    def get_current_user(self, token: Optional[str]) -> Optional[User]:
        """
        Returns the authenticated user or None, if no token was provided
        Supported formats:
        
        1. Mock tokens for tests/local dev (not real JWTs):
           - "provider:alice@example.com"
           - "admin:admin@example.com"
           - "buyer:buyer@example.com"

        2. Supabase JWTs:
           - HS256-signed, with 'sub', 'email' (or user_metadata.email),
             and optional user_metadata.role.
        """
        if not token:
            return None

        token = token.strip()

        #strip Bearer prefix if it leaked through
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        #Mock token: "provider:provider@example.com"
        if ":" in token:
            role_str, email = token.split(":", 1)
            role_str = role_str.lower()

            return self._get_or_create_user(
                sub=email,
                email=email,
                role=role_str,
            )

        #Real Supabase JWT
        payload = self._decode_supabase_jwt(token)

        sub = payload.get("sub")
        #handle Supabase email nesting in user_metadata
        email = payload.get("email") or payload.get("user_metadata", {}).get("email")
        metadata = payload.get("user_metadata") or {}
        role = metadata.get("role")

        if not sub or not email:
            raise ValueError("Invalid JWT payload: missing 'sub' or 'email'.")

        return self._get_or_create_user(sub=sub, email=email, role=role)


def get_auth_service(
    db: Session = Depends(get_db),
    users_public: UsersPublic = Depends(get_users_public)
) -> AuthService:
    return AuthService(db, users_public)