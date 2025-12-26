from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from uuid import UUID

from .models import AccessCredential


class AccessCredentialRepository:

    def create(self, db: Session, booking_id, vpn_config_uri, ssh_public_key_fingerprint):
        """"Create credentials with booking_id as reference information"""
        credential = AccessCredential(
            booking_id=booking_id,
            vpn_config_uri=vpn_config_uri,
            ssh_public_key_fingerprint=ssh_public_key_fingerprint,
        )

        db.add(credential)
        db.commit()
        db.refresh(credential)

        return credential

    def get_by_booking_id(self, db: Session, booking_id: UUID):
        stmt = select(AccessCredential).where(
            AccessCredential.booking_id == booking_id
        )
        result = db.execute(stmt)
        return result.scalars().all()

    def mark_revoked(self, db: Session, credential_id: UUID):
        """
        This marks a credential as revoked by setting a revoked_at timestamp.
        This does not revoke on a provider (for AccessCredentialsService).
        """
        stmt = select(AccessCredential).where(AccessCredential.id == credential_id)
        result = db.execute(stmt)
        credential = result.scalar_one_or_none()

        if credential is None:
            return None

        credential.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(credential)

        return credential