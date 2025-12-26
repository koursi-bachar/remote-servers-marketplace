"""
Repository methods for looking up and creating application users.
These are keyed by supabase_id (the "sub" field from Supabase JWTs).
This file is the link between authentication and the DB model.
"""

from sqlalchemy.orm import Session
from app.users.models import User, UserRole

import uuid


class UsersRepository:
    def get_user_by_supabase_id(self, db: Session, sub: str) -> User | None:
        """
        supabase_id corresponds to the JWT 'sub' claim.
        This identifies the same user across login sessions.
        """
        return db.query(User).filter_by(supabase_id=sub).first()

    def create_user(
        self,
        db: Session,
        email: str,
        supabase_id: str | None = None,
        role: UserRole = UserRole.BUYER,
    ) -> User:
        """
        When testing locally without real Supabase, we generate a fake UUID 
        so the user can still be uniquely identified.
        """
        if supabase_id is None:
            supabase_id = str(uuid.uuid4())  #auto-generate for testing

        new_user = User(
            supabase_id=supabase_id,
            email=email,
            role=role,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def get_or_create_user_by_supabase_id(
        self,
        db: Session,
        sub: str,
        email: str,
        role: str | None,
    ) -> User:
        """
        This approach means accounts are auto-provisioned on first login.
        If we want explicit admin approval or onboarding flows, this is
        the place to change the behavior.
        """
        user = self.get_user_by_supabase_id(db, sub)
        if user:
            return user
        """
        Supabase allows attaching a user role in JWT metadata.
        If present, we convert it to our internal enum. Otherwise,
        every new user defaults to BUYER.
        """
        role_enum = UserRole(role.lower()) if role else UserRole.BUYER
        return self.create_user(db, supabase_id=sub, email=email, role=role_enum)