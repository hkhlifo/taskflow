import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_email(
    recipient: str,
    subject: str,
    body: str,
):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise RuntimeError("Gmail configuration is missing")

    message = EmailMessage()
    message["From"] = GMAIL_USER
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(message)