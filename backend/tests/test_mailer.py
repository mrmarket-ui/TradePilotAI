import logging
import ssl

import pytest

from services.mailer import sender, templates
from services.mailer.sender import Mail, MailConfigError


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ["EMAIL_BACKEND", "SMTP_HOST", "SMTP_PORT", "SMTP_SECURITY", "SMTP_USERNAME",
                 "SMTP_PASSWORD", "EMAIL_FROM", "EMAIL_REPLY_TO", "APP_ENV", "FOUNDER_SIGNATURE"]:
        monkeypatch.delenv(name, raising=False)


# ---------------- templates ----------------

def test_login_code_email_has_the_code_but_not_in_the_subject():
    mail = templates.login_code_mail(to="a@b.com", full_name="Neliswa Mzimba", code="482915", minutes=10)
    assert "482915" in mail.text and "482915" in mail.html
    assert "482915" not in mail.subject
    assert "10 minutes" in mail.text
    assert "never ask you for this code" in mail.text
    assert "Hi Neliswa," in mail.text


def test_user_supplied_names_cannot_inject_html():
    mail = templates.login_code_mail(to="a@b.com", full_name='<script>alert(1)</script> Evil', code="111111", minutes=10)
    assert "<script>" not in mail.html
    assert "&lt;script&gt;" in mail.html


def test_name_falls_back_to_the_email_name():
    assert templates.friendly_name(None, "neliswa@example.com") == "Neliswa"
    assert templates.friendly_name("  ", "x@example.com") == "X"
    assert templates.friendly_name("Neliswa Theophollus Mzimba", "x@example.com") == "Neliswa"
    assert templates.friendly_name(None, "") == "trader"


def test_welcome_email_links_to_the_app_and_is_attribute_safe():
    mail = templates.welcome_mail(to="a@b.com", full_name="Neliswa", app_url='https://app.example.com/?a="1"')
    assert 'https://app.example.com/?a="1"' in mail.text
    assert "&quot;" in mail.html and 'href="https://app.example.com/?a="1""' not in mail.html
    assert mail.subject == "Welcome to TradePilot AI"
    assert "Trade Smarter. Think Better. Evolve Daily." in mail.text


def test_reset_email_has_the_link_but_not_in_the_subject():
    link = "https://app.example.com/reset-password?token=abc"
    mail = templates.password_reset_mail(to="a@b.com", full_name=None, link=link, minutes=30)
    assert link in mail.text and "token=abc" in mail.html
    assert "token" not in mail.subject
    assert "30 minutes" in mail.text


def test_password_changed_email():
    mail = templates.password_changed_mail(to="a@b.com", full_name="Neliswa")
    assert "was changed" in mail.subject
    assert "signed out everywhere" in mail.text


def test_signature_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv("FOUNDER_SIGNATURE", "Neliswa, Founder of TradePilot AI")
    mail = templates.welcome_mail(to="a@b.com", full_name="X", app_url="https://app.example.com")
    assert "Neliswa, Founder of TradePilot AI" in mail.text
    assert templates.login_code_mail(to="a@b.com", full_name="X", code="1", minutes=10).text.endswith(
        "Neliswa, Founder of TradePilot AI")


def test_default_signature_is_the_team(monkeypatch):
    mail = templates.welcome_mail(to="a@b.com", full_name="X", app_url="https://app.example.com")
    assert "The TradePilot AI team" in mail.text


# ---------------- sending ----------------

class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=None, context=None):
        self.host, self.port, self.context, self.calls, self.sent = host, port, context, [], None
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self, context=None):
        self.calls.append("starttls")
        self.tls_context = context

    def login(self, user, password):
        self.calls.append(("login", user, password))

    def send_message(self, message):
        self.calls.append("send")
        self.sent = message


class FakeSMTPSSL(FakeSMTP):
    pass


@pytest.fixture
def fake_smtp(monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(sender.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(sender.smtplib, "SMTP_SSL", FakeSMTPSSL)
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("EMAIL_FROM", "TradePilot AI <no-reply@example.com>")
    return FakeSMTP


MAIL = Mail(to="user@example.com", subject="Hello", text="plain body 482915", html="<p>html body</p>")


def test_the_default_backend_depends_on_smtp_being_configured(monkeypatch):
    assert sender.backend_name() == "console"
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    assert sender.backend_name() == "smtp"
    monkeypatch.setenv("EMAIL_BACKEND", "console")
    assert sender.backend_name() == "console"


def test_smtp_uses_starttls_before_logging_in(fake_smtp, monkeypatch):
    monkeypatch.setenv("SMTP_USERNAME", "apikey")
    monkeypatch.setenv("SMTP_PASSWORD", "s3cret")
    sender.send_email(MAIL)
    server = fake_smtp.instances[0]
    assert (server.host, server.port) == ("smtp.example.com", 587)
    assert server.calls == ["starttls", ("login", "apikey", "s3cret"), "send"]
    # the secure connection must verify the server's certificate and hostname
    assert server.tls_context.verify_mode == ssl.CERT_REQUIRED
    assert server.tls_context.check_hostname is True


def test_ssl_mode_uses_an_encrypted_connection_from_the_start(fake_smtp, monkeypatch):
    monkeypatch.setenv("SMTP_SECURITY", "ssl")
    monkeypatch.setenv("SMTP_PORT", "465")
    sender.send_email(MAIL)
    server = fake_smtp.instances[0]
    assert isinstance(server, FakeSMTPSSL) and server.port == 465
    assert "starttls" not in server.calls
    assert server.context.verify_mode == ssl.CERT_REQUIRED
    assert server.context.check_hostname is True


def test_unencrypted_smtp_is_refused(fake_smtp, monkeypatch):
    monkeypatch.setenv("SMTP_SECURITY", "none")
    with pytest.raises(MailConfigError):
        sender.send_email(MAIL)
    assert fake_smtp.instances == []


def test_the_message_has_the_right_headers_and_both_versions(fake_smtp, monkeypatch):
    monkeypatch.setenv("EMAIL_REPLY_TO", "help@example.com")
    sender.send_email(MAIL)
    message = fake_smtp.instances[0].sent
    assert message["To"] == "user@example.com"
    assert message["From"] == "TradePilot AI <no-reply@example.com>"
    assert message["Subject"] == "Hello"
    assert message["Reply-To"] == "help@example.com"
    assert message["Auto-Submitted"] == "auto-generated"
    kinds = [part.get_content_type() for part in message.walk()]
    assert "text/plain" in kinds and "text/html" in kinds


def test_a_missing_sender_address_is_an_error(fake_smtp, monkeypatch):
    monkeypatch.delenv("EMAIL_FROM")
    with pytest.raises(MailConfigError):
        sender.send_email(MAIL)


def test_header_injection_is_blocked(fake_smtp):
    bad = Mail(to="user@example.com", subject="Hi\nBcc: attacker@evil.com", text="x", html="x")
    assert sender.send_email_safely(bad) is False
    assert fake_smtp.instances == []
    bad_to = Mail(to="user@example.com\nBcc: attacker@evil.com", subject="Hi", text="x", html="x")
    assert sender.send_email_safely(bad_to) is False


def test_the_console_backend_never_runs_in_production(monkeypatch):
    monkeypatch.setenv("EMAIL_BACKEND", "console")
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(MailConfigError):
        sender.send_email(MAIL)
    assert sender.send_email_safely(MAIL) is False


def test_the_console_backend_prints_in_development(caplog):
    with caplog.at_level(logging.WARNING, logger="tradepilot.mailer"):
        sender.send_email(MAIL)
    assert "DEV EMAIL" in caplog.text and "482915" in caplog.text


def test_unknown_backends_are_refused(monkeypatch):
    monkeypatch.setenv("EMAIL_BACKEND", "carrier-pigeon")
    with pytest.raises(MailConfigError):
        sender.send_email(MAIL)


def test_failures_are_reported_without_leaking_the_message(fake_smtp, monkeypatch, caplog):
    def explode(self, message):
        raise OSError("connection reset")

    monkeypatch.setattr(FakeSMTP, "send_message", explode)
    with caplog.at_level(logging.ERROR, logger="tradepilot.mailer"):
        assert sender.send_email_safely(MAIL) is False
    assert "OSError" in caplog.text
    assert "482915" not in caplog.text and "user@example.com" not in caplog.text
    assert "@example.com" in caplog.text