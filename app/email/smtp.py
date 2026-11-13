"""Generic SMTP email sender with no project-specific templates."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import get_settings


def send_email(recipient: str, subject: str, text_body: str, html_body: str | None = None) -> None:
    settings = get_settings()
    if not settings.smtp_user or not settings.smtp_password or not settings.smtp_from_email:
        raise RuntimeError("SMTP_USER, SMTP_PASSWORD, and SMTP_FROM_EMAIL must be configured")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
        server.ehlo()
        if settings.smtp_use_starttls:
            server.starttls()
            server.ehlo()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)
