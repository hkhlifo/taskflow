
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """Send an email using Gmail's SMTP server.

    Args:
        recipient: Email address of the recipient.
        subject: Subject line of the email.
        body: Plain-text content of the email.

    Raises:
        RuntimeError: If Gmail credentials are not configured.
        smtplib.SMTPException: If an SMTP-related error occurs.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise RuntimeError(
            "Missing Gmail configuration. "
            "Set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file."
        )

    message = EmailMessage()
    message["From"] = GMAIL_USER
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(message)
