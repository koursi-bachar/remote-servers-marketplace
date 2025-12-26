from typing import Protocol


class EmailPort(Protocol):
    """
    Abstract interface for sending emails.
    Concrete adapters (SendGrid, SMTP)
    must implement this.
    """
    def send_email(self, to: str, subject: str, html_body: str) -> None:
        """
        Send an email to a recipient.
        to: Recipient email address
        subject: Email subject line
        html_body: Full HTML email body
        """
        ...