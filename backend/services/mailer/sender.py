"""
TradePilot AI email sending.

Works with any SMTP provider, so the provider can be changed without code
changes. Settings come from environment variables:

    EMAIL_BACKEND    smtp | console   (default: smtp if SMTP_HOST is set)
    SMTP_HOST, SMTP_PORT (587), SMTP_SECURITY (starttls | ssl)
    SMTP_USERNAME, SMTP_PASSWORD
    EMAIL_FROM       e.g. "TradePilot AI <no-reply@your-domain.com>"
    EMAIL_REPLY_TO   optional
    APP_ENV          "production" refuses to use the console backend

The console backend prints emails (including login codes) to the server log
and exists only for local development.
"""

from __future__ import annotations

import logging
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage

logger = logging.getLogger("tradepilot.mailer")


class MailConfigError(RuntimeError):
    """Raised when email is not configured safely."""


@dataclass(frozen=True)
class Mail:
    to: str
    subject: str
    text: str
    html: str


def _is_production() -> bool:
    return os.getenv("APP_ENV", "development").strip().lower() == "production"


def backend_name() -> str:
    explicit = os.getenv("EMAIL_BACKEND", "").strip().lower()

    if explicit:
        return explicit

    return "smtp" if os.getenv("SMTP_HOST", "").strip() else "console"


def build_message(mail: Mail) -> EmailMessage:
    sender = os.getenv("EMAIL_FROM", "").strip()

    if not sender:
        raise MailConfigError("EMAIL_FROM is not configured.")

    message = EmailMessage()

    # EmailMessage rejects line breaks in headers, which blocks header injection.
    message["From"] = sender
    message["To"] = mail.to
    message["Subject"] = mail.subject
    message["Auto-Submitted"] = "auto-generated"
    message["X-Auto-Response-Suppress"] = "All"

    reply_to = os.getenv("EMAIL_REPLY_TO", "").strip()

    if reply_to:
        message["Reply-To"] = reply_to

    message.set_content(mail.text)
    message.add_alternative(mail.html, subtype="html")

    return message


def _send_smtp(message: EmailMessage) -> None:
    host = os.getenv("SMTP_HOST", "").strip()

    if not host:
        raise MailConfigError("SMTP_HOST is not configured.")

    port = int(os.getenv("SMTP_PORT", "587"))
    security = os.getenv("SMTP_SECURITY", "starttls").strip().lower()

    if security not in ("starttls", "ssl"):
        raise MailConfigError("SMTP_SECURITY must be 'starttls' or 'ssl'.")

    context = ssl.create_default_context()

    if security == "ssl":
        server = smtplib.SMTP_SSL(host, port, timeout=15, context=context)
    else:
        server = smtplib.SMTP(host, port, timeout=15)

    with server:
        if security == "starttls":
            server.starttls(context=context)

        username = os.getenv("SMTP_USERNAME", "").strip()

        if username:
            server.login(username, os.getenv("SMTP_PASSWORD", ""))

        server.send_message(message)


def send_email(mail: Mail) -> None:
    """Sends one email. Raises on any failure."""

    backend = backend_name()

    if backend == "console":
        if _is_production():
            raise MailConfigError(
                "The console email backend is not allowed in production."
            )

        logger.warning(
            "[DEV EMAIL] To: %s | Subject: %s\n%s",
            mail.to,
            mail.subject,
            mail.text,
        )
        return

    if backend != "smtp":
        raise MailConfigError(f"Unknown EMAIL_BACKEND '{backend}'.")

    _send_smtp(build_message(mail))


def send_email_safely(mail: Mail) -> bool:
    """Sends one email and never raises. Logs only the error type, never the
    message body (which can contain a login code or a reset link)."""

    try:
        send_email(mail)
        return True
    except Exception as exc:
        logger.error("Email to %s failed: %s", _domain_only(mail.to), type(exc).__name__)
        return False


def _domain_only(address: str) -> str:
    return "@" + address.split("@")[-1] if "@" in address else "(invalid address)"