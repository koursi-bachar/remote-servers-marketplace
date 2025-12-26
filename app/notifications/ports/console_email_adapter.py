from .email_port import EmailPort


class ConsoleEmailAdapter(EmailPort):
    """
    Development / testing adapter.
    Prints emails to the console instead of sending.
    """
    def send_email(self, to: str, subject: str, html_body: str) -> None:
        print("\n================ MOCK EMAIL ================")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print("Body:")
        print(html_body)
        print("===========================================\n")