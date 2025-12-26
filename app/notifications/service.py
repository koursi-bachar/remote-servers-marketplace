import os
from typing import Dict

from jinja2 import Environment, FileSystemLoader

from .ports.email_port import EmailPort


class NotificationsService:
    def __init__(self, email_port: EmailPort, template_dir: str):
        self.email_port = email_port

        # Better path handling
        from pathlib import Path
        
        template_path = Path(template_dir)
        if not template_path.is_absolute():
            # If relative path, make it absolute relative to current file
            template_path = Path(__file__).parent / template_dir
        
        print(f"Loading templates from: {template_path}")
        
        # Ensure directory exists
        template_path.mkdir(parents=True, exist_ok=True)
        
        # Load Jinja2 environment for email templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=True
        )

    # Internal render and send helpers
    def _render(self, template_name: str, context: Dict) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    def _send(self, to: str, subject: str, template: str, context: Dict):
        html = self._render(template, context)
        self.email_port.send_email(to, subject, html)

    # Booking emails
    def send_booking_confirmation(self, user, booking):
        self._send(
            to=user.email,
            subject=f"Booking Confirmed — {booking.id}",
            template="booking_confirmed.html",
            context={"user": user, "booking": booking},
        )

    def send_booking_activated(self, user, booking):
        self._send(
            to=user.email,
            subject="Your Machine is Now Active",
            template="booking_activated.html",
            context={"user": user, "booking": booking},
        )

    def send_booking_completed(self, user, booking):
        self._send(
            to=user.email,
            subject="Your Booking is Complete",
            template="booking_completed.html",
            context={"user": user, "booking": booking},
        )

    def send_booking_cancelled(self, user, booking, reason: str):
        self._send(
            to=user.email,
            subject="Your Booking Was Cancelled",
            template="booking_cancelled.html",
            context={"user": user, "booking": booking, "reason": reason},
        )

    # Payment emails
    def send_payment_captured(self, user, payment):
        self._send(
            to=user.email,
            subject="Payment Receipt",
            template="payment_captured.html",
            context={"user": user, "payment": payment},
        )

    def send_payment_failed(self, user, payment):
        self._send(
            to=user.email,
            subject="Payment Failed",
            template="payment_failed.html",
            context={"user": user, "payment": payment},
        )

    def send_refund_issued(self, user, payment):
        self._send(
            to=user.email,
            subject="Refund Issued",
            template="refund_issued.html",
            context={"user": user, "payment": payment},
        )

    # Credentials emails
    def send_credentials_issued(self, user, credential):
        self._send(
            to=user.email,
            subject="Your Access Credentials",
            template="credentials_issued.html",
            context={"user": user, "credential": credential},
        )

    def send_credentials_revoked(self, user, credential):
        self._send(
            to=user.email,
            subject="Your Credentials Were Revoked",
            template="credentials_revoked.html",
            context={"user": user, "credential": credential},
        )

    # Dispute emails
    def send_dispute_opened(self, dispute, user):
        self._send(
            to=user.email,
            subject="A Dispute Has Been Opened",
            template="dispute_opened.html",
            context={"dispute": dispute, "user": user},
        )

    def send_dispute_resolved(self, dispute, user):
        self._send(
            to=user.email,
            subject="Your Dispute Was Resolved",
            template="dispute_resolved.html",
            context={"dispute": dispute, "user": user},
        )

    # Compliance emails
    def send_wipe_proof_submitted(self, provider, booking, attestation):
        self._send(
            to=provider.email,
            subject="Wipe Proof Submitted",
            template="wipe_proof_submitted.html",
            context={"provider": provider, "booking": booking, "attestation": attestation},
        )

    def send_wipe_failure(self, provider, booking):
        self._send(
            to=provider.email,
            subject="Machine Wipe Failure",
            template="wipe_failure.html",
            context={"provider": provider, "booking": booking},
        )

    def send_provider_suspended(self, provider, reason):
        self._send(
            to=provider.email,
            subject="Your Provider Account Has Been Suspended",
            template="provider_suspended.html",
            context={"provider": provider, "reason": reason},
        )

    # Invoice emails
    def send_invoice_generated(self, organization, invoice):
        self._send(
            to=organization.billing_email,
            subject="Invoice Generated",
            template="invoice_generated.html",
            context={"organization": organization, "invoice": invoice},
        )

    def send_invoice_finalized(self, organization, invoice):
        self._send(
            to=organization.billing_email,
            subject="Invoice Finalized",
            template="invoice_finalized.html",
            context={"organization": organization, "invoice": invoice},
        )

    # Provider/metrics Alerts
    def send_provider_alert(self, provider, message: str):
        self._send(
            to=provider.email,
            subject="Provider Alert",
            template="provider_alert.html",
            context={"provider": provider, "message": message},
        )

    def send_machine_health_anomaly(self, provider, machine, details: str):
        self._send(
            to=provider.email,
            subject="Machine Health Anomaly Detected",
            template="machine_health_anomaly.html",
            context={"provider": provider, "machine": machine, "details": details},
        )

    def send_machine_offline(self, provider, machine):
        self._send(
            to=provider.email,
            subject="Machine Offline",
            template="machine_offline.html",
            context={"provider": provider, "machine": machine},
        )