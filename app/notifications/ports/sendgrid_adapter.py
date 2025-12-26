import requests
from .email_port import EmailPort


class SendGridEmailAdapter(EmailPort):
    """
    Production adapter using SendGrid's API.
    """
    SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, api_key: str, sender_email: str):
        self.api_key = api_key
        self.sender_email = sender_email

    def send_email(self, to: str, subject: str, html_body: str) -> None:
        payload = {
            "personalizations": [
                {
                    "to": [{"email": to}],
                    "subject": subject,
                }
            ],
            "from": {"email": self.sender_email},
            "content": [
                {
                    "type": "text/html",
                    "value": html_body
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(self.SENDGRID_API_URL, json=payload, headers=headers)

        if response.status_code >= 400:
            raise RuntimeError(
                f"SendGrid API error {response.status_code}: {response.text}"
            )