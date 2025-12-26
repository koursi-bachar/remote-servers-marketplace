import os
from pathlib import Path

from .service import NotificationsService
from .ports.console_email_adapter import ConsoleEmailAdapter


class NotificationsPublic:
    """Protocol defining the public interface for notifications queries."""
    def __init__(self, service: NotificationsService):
        self.service = service

    # Booking events
    def booking_confirmed(self, user, booking):
        self.service.send_booking_confirmation(user, booking)

    def booking_activated(self, user, booking):
        self.service.send_booking_activated(user, booking)

    def booking_completed(self, user, booking):
        self.service.send_booking_completed(user, booking)

    def booking_cancelled(self, user, booking, reason):
        self.service.send_booking_cancelled(user, booking, reason)

    # Payment events
    def payment_captured(self, user, payment):
        self.service.send_payment_captured(user, payment)

    def payment_failed(self, user, payment):
        self.service.send_payment_failed(user, payment)

    def refund_issued(self, user, payment):
        self.service.send_refund_issued(user, payment)

    # Credential events
    def credentials_issued(self, user, credential):
        self.service.send_credentials_issued(user, credential)

    def credentials_revoked(self, user, credential):
        self.service.send_credentials_revoked(user, credential)

    # Dispute events
    def dispute_opened(self, dispute, user):
        self.service.send_dispute_opened(dispute, user)

    def dispute_resolved(self, dispute, user):
        self.service.send_dispute_resolved(dispute, user)

    # Compliance events
    def wipe_proof_submitted(self, provider, booking, attestation):
        self.service.send_wipe_proof_submitted(provider, booking, attestation)

    def wipe_failure(self, provider, booking):
        self.service.send_wipe_failure(provider, booking)

    def provider_suspended(self, provider, reason):
        self.service.send_provider_suspended(provider, reason)

    # Invoice events
    def invoice_generated(self, organization, invoice):
        self.service.send_invoice_generated(organization, invoice)

    def invoice_finalized(self, organization, invoice):
        self.service.send_invoice_finalized(organization, invoice)

    # Provider/metrics alerts
    def provider_alert(self, provider, message):
        self.service.send_provider_alert(provider, message)

    def machine_health_anomaly(self, provider, machine, details):
        self.service.send_machine_health_anomaly(provider, machine, details)

    def machine_offline(self, provider, machine):
        self.service.send_machine_offline(provider, machine)

def get_notifications_public():
    """Dependency injection provider for NotificationsService interface."""
    # Better path calculation
    current_dir = Path(__file__).parent
    template_dir = current_dir / "templates"
    
    # Ensure the directory exists
    template_dir.mkdir(exist_ok=True)

    # Dev/testing: Console adapter
    email_adapter = ConsoleEmailAdapter()

    service = NotificationsService(
        email_port=email_adapter,
        template_dir=str(template_dir),
    )

    return NotificationsPublic(service)