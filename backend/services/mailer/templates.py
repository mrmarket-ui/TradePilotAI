"""
TradePilot AI email templates.

Every value that comes from a user (name, email) is HTML-escaped before it is
placed in the HTML version. Subjects never contain codes or links, because
subjects show up in lock-screen notifications and logs.
"""

from __future__ import annotations

import os
from html import escape

from services.mailer.sender import Mail

BRAND = "TradePilot AI"
MOTTO = "Trade Smarter. Think Better. Evolve Daily."

_BLUE = "#3b82f6"
_NAVY = "#0b1120"


def friendly_name(full_name: str | None, email: str) -> str:
    name = (full_name or "").strip().split(" ")[0]

    if name:
        return name

    local = (email or "").split("@")[0]

    return local[:1].upper() + local[1:] if local else "trader"


def _signature() -> str:
    return os.getenv("FOUNDER_SIGNATURE", "").strip() or f"The {BRAND} team"


def _layout(preheader: str, heading: str, body_html: str) -> str:
    return f"""<!doctype html>
<html>
<body style="margin:0;padding:0;background:#eef2f7;font-family:Segoe UI,Arial,sans-serif;">
<span style="display:none;max-height:0;overflow:hidden;opacity:0;">{escape(preheader)}</span>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#eef2f7;padding:24px 12px;">
<tr><td align="center">
<table role="presentation" width="560" cellspacing="0" cellpadding="0" style="max-width:560px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;">
<tr><td style="background:{_NAVY};padding:22px 28px;color:#ffffff;font-size:20px;font-weight:600;">{BRAND}</td></tr>
<tr><td style="padding:28px;color:#1f2937;font-size:15px;line-height:1.6;">
<h1 style="margin:0 0 16px;font-size:22px;color:{_NAVY};">{escape(heading)}</h1>
{body_html}
</td></tr>
<tr><td style="padding:18px 28px;background:#f8fafc;color:#6b7280;font-size:12px;line-height:1.5;">
{escape(MOTTO)}<br>{BRAND} provides educational analytics, not financial advice.
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def _button(label: str, url: str) -> str:
    return (
        f'<p style="margin:24px 0;"><a href="{escape(url, quote=True)}" '
        f'style="background:{_BLUE};color:#ffffff;text-decoration:none;'
        f'padding:12px 22px;border-radius:10px;font-weight:600;display:inline-block;">'
        f"{escape(label)}</a></p>"
    )


def login_code_mail(*, to: str, full_name: str | None, code: str, minutes: int) -> Mail:
    name = friendly_name(full_name, to)

    text = (
        f"Hi {name},\n\n"
        f"Your {BRAND} login code is: {code}\n\n"
        f"It expires in {minutes} minutes and can be used once.\n\n"
        f"If you did not just try to sign in, someone may know your password. "
        f"Reset it right away. {BRAND} will never ask you for this code by "
        f"phone, chat or email.\n\n"
        f"{_signature()}"
    )

    body = (
        f"<p>Hi {escape(name)},</p>"
        f"<p>Use this code to finish signing in:</p>"
        f'<p style="margin:20px 0;font-size:32px;letter-spacing:8px;font-weight:700;'
        f'color:{_NAVY};font-family:Consolas,monospace;">{escape(code)}</p>'
        f"<p>It expires in {int(minutes)} minutes and can be used once.</p>"
        f"<p><strong>If you did not just try to sign in</strong>, someone may know "
        f"your password. Reset it right away. {BRAND} will never ask you for this "
        f"code by phone, chat or email.</p>"
        f"<p>{escape(_signature())}</p>"
    )

    return Mail(
        to=to,
        subject=f"Your {BRAND} login code",
        text=text,
        html=_layout("Your one-time login code", "Confirm it is you", body),
    )


def welcome_mail(*, to: str, full_name: str | None, app_url: str) -> Mail:
    name = friendly_name(full_name, to)

    text = (
        f"Welcome to {BRAND}, {name}!\n\n"
        f"Your account has been created. To keep it safe, we will email you a "
        f"one-time code every time you sign in.\n\n"
        f"Good places to start:\n"
        f"  - Log your first trades in the Trade Journal\n"
        f"  - Explore Macro Intelligence\n"
        f"  - Build your first strategy in Strategy Lab\n\n"
        f"Open your workspace: {app_url}\n\n"
        f"{MOTTO}\n{_signature()}"
    )

    body = (
        f"<p>Welcome, {escape(name)}! Your account has been created.</p>"
        f"<p>To keep it safe, we email you a one-time code every time you sign in.</p>"
        f"<p>Good places to start:</p>"
        f"<ul><li>Log your first trades in the Trade Journal</li>"
        f"<li>Explore Macro Intelligence</li>"
        f"<li>Build your first strategy in Strategy Lab</li></ul>"
        f"{_button('Open your workspace', app_url)}"
        f"<p>{escape(_signature())}</p>"
    )

    return Mail(
        to=to,
        subject=f"Welcome to {BRAND}",
        text=text,
        html=_layout("Your account is ready", f"Welcome to {BRAND}", body),
    )


def password_reset_mail(*, to: str, full_name: str | None, link: str, minutes: int) -> Mail:
    name = friendly_name(full_name, to)

    text = (
        f"Hi {name},\n\n"
        f"We received a request to reset your {BRAND} password. Open this link "
        f"within {minutes} minutes to choose a new one:\n\n{link}\n\n"
        f"If you did not ask for this, ignore this email. Your password stays "
        f"the same and the link stops working after it is used or expires.\n\n"
        f"{_signature()}"
    )

    body = (
        f"<p>Hi {escape(name)},</p>"
        f"<p>We received a request to reset your {BRAND} password. Use the button "
        f"below within {int(minutes)} minutes to choose a new one.</p>"
        f"{_button('Choose a new password', link)}"
        f"<p>If you did not ask for this, ignore this email. Your password stays "
        f"the same, and the link stops working after it is used or expires.</p>"
        f"<p>{escape(_signature())}</p>"
    )

    return Mail(
        to=to,
        subject=f"Reset your {BRAND} password",
        text=text,
        html=_layout("Reset your password", "Reset your password", body),
    )


def password_changed_mail(*, to: str, full_name: str | None) -> Mail:
    name = friendly_name(full_name, to)

    text = (
        f"Hi {name},\n\n"
        f"Your {BRAND} password was just changed and you were signed out "
        f"everywhere.\n\nIf this was you, no action is needed. If it was not, "
        f"reset your password again immediately and contact us.\n\n"
        f"{_signature()}"
    )

    body = (
        f"<p>Hi {escape(name)},</p>"
        f"<p>Your {BRAND} password was just changed and you were signed out everywhere.</p>"
        f"<p>If this was you, no action is needed. <strong>If it was not</strong>, "
        f"reset your password again immediately and contact us.</p>"
        f"<p>{escape(_signature())}</p>"
    )

    return Mail(
        to=to,
        subject=f"Your {BRAND} password was changed",
        text=text,
        html=_layout("Password changed", "Your password was changed", body),
    )