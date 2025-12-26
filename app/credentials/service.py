from fastapi import Depends
from app.database import get_db
from sqlalchemy.orm import Session

from .repository import AccessCredentialRepository
from .issuer import get_credential_issuer, CredentialIssuer

from app.notifications.public import NotificationsPublic, get_notifications_public


class AccessCredentialsService:
    
    def __init__(
        self,
        db: Session,
        repo: AccessCredentialRepository,
        issuer: CredentialIssuer,
        notifications_public: NotificationsPublic,  
    ):
        self.db = db
        self.repo = repo
        self.issuer = issuer
        self.notifications = notifications_public

    def issue_for_booking(self, booking):
        """
        Issues credentials for a booking, but only if the booking is ACTIVE.
        """
        user = booking.buyer
        machine = booking.listing.machine

        #Issue via the dedicated credentials issuer
        payload = self.issuer.issue(
            booking=booking,
            user=user,
            machine=machine,
        )

        saved = self.repo.create(
            self.db,
            booking_id=booking.id,
            vpn_config_uri=payload.vpn_config_uri,
            ssh_public_key_fingerprint=payload.ssh_public_key_fingerprint,
        )

        self.notifications.credentials_issued(booking.buyer, saved)

        return saved

    def revoke_for_booking(self, booking):
        """
        Revoke credentials for a booking.
        """
        credentials = self.repo.get_by_booking_id(self.db, booking.id)

        if not credentials:
            return []
        
        revoked_list = []

        for credential in credentials:
            self.issuer.revoke(credential)
            updated = self.repo.mark_revoked(self.db, credential.id)
            revoked_list.append(updated)

        self.notifications.credentials_revoked(booking.buyer, updated)

        return revoked_list

    def get_for_booking(self, booking):
        """
        Return credentials for displaying or auditing.
        """
        return self.repo.get_by_booking_id(self.db, booking.id)

def get_access_credential_service(
    db: Session = Depends(get_db),
    issuer: CredentialIssuer = Depends(get_credential_issuer),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> AccessCredentialsService:

    repo = AccessCredentialRepository()

    return AccessCredentialsService(
        db=db,
        repo=repo,
        issuer=issuer,
        notifications_public=notifications_public,
    )