"""
TradePilot AI sign-in logic.

The routes in routes/v1/auth.py stay thin; everything that decides whether a
password, a code or a reset link is acceptable lives here, so it can be tested
without a web server.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.auth_security import AuthChallenge, AuthSecurity, PasswordResetToken
from models.user import User
from services.auth_service import (
    burn_password_time,
    hash_password,
    verify_and_update,
)
from services.security import otp
from services.security.password_policy import validate_password
from services.security.tokens import (
    RESET_TOKEN_TTL_MINUTES,
    hash_token,
    is_plausible_token,
    new_token,
)

MAX_PASSWORD_INPUT = 1024


class AuthError(Exception):
    def __init__(self, status_code: int, code: str, message: str, **extra):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.extra = extra

    def detail(self) -> dict:
        return {"code": self.code, "message": self.message, **self.extra}


def _now() -> datetime:
    return otp.utc_now()


def normalise_email(email: object) -> str:
    return str(email or "").strip().lower()


def clean_name(value: object) -> str | None:
    text = re.sub(r"[\x00-\x1f\x7f]", "", str(value or ""))
    text = re.sub(r"\s+", " ", text).strip()[:80]

    return text or None


def find_user(db: Session, email: object) -> User | None:
    return (
        db.query(User)
        .filter(func.lower(User.email) == normalise_email(email))
        .first()
    )


def get_security(db: Session, user_id: int) -> AuthSecurity:
    row = db.query(AuthSecurity).filter(AuthSecurity.user_id == user_id).first()

    if row is None:
        row = AuthSecurity(user_id=user_id, token_version=0)
        db.add(row)

        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            row = (
                db.query(AuthSecurity)
                .filter(AuthSecurity.user_id == user_id)
                .one()
            )

    return row


# ------------------------------------------------------------------ #
# Passwords and registration                                          #
# ------------------------------------------------------------------ #

def authenticate(db: Session, email: str, password: str) -> User:
    """Checks the password. Never reveals whether the email exists."""

    user = find_user(db, email)
    password = password or ""

    if user is None or len(password) > MAX_PASSWORD_INPUT:
        burn_password_time(password[:MAX_PASSWORD_INPUT])
        raise AuthError(401, "INVALID_CREDENTIALS", "Invalid email or password.")

    correct, upgraded_hash = verify_and_update(password, user.password_hash)

    if not correct:
        raise AuthError(401, "INVALID_CREDENTIALS", "Invalid email or password.")

    if upgraded_hash:
        user.password_hash = upgraded_hash
        db.commit()

    if not user.is_active:
        raise AuthError(
            403,
            "ACCOUNT_INACTIVE",
            "This account has been suspended or deactivated.",
        )

    return user


def register_user(
    db: Session,
    *,
    email: str,
    password_hash: str,
    full_name: str | None,
) -> User | None:
    """Creates the account, or returns None if the email is already taken."""

    if find_user(db, email) is not None:
        return None

    user = User(
        email=normalise_email(email),
        password_hash=password_hash,
        full_name=full_name,
    )

    db.add(user)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return None

    db.add(AuthSecurity(user_id=user.id, token_version=0, terms_accepted_at=_now()))
    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------------------------ #
# Emailed login codes                                                 #
# ------------------------------------------------------------------ #

def start_challenge(
    db: Session,
    user_id: int | None,
    ip: str | None,
) -> tuple[AuthChallenge, str]:
    """Creates a login code. With user_id=None it makes a decoy that can never succeed."""

    now = _now()
    challenge_id = otp.new_challenge_id()
    code = otp.generate_code()

    row = AuthChallenge(
        challenge_id=challenge_id,
        user_id=user_id,
        purpose="login",
        code_hash=otp.hash_code(code, challenge_id),
        expires_at=otp.expiry_time(now),
        attempts=0,
        resend_count=0,
        last_sent_at=now,
        created_at=now,
        ip_address=ip,
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return row, code


def _bad_code(attempts_left: int | None = None) -> AuthError:
    extra = {} if attempts_left is None else {"attempts_left": attempts_left}

    return AuthError(400, "CODE_INVALID", "That code is not correct.", **extra)


def verify_challenge(db: Session, challenge_id: str, submitted: str) -> int:
    """Checks an emailed code. Returns the user id, or raises AuthError."""

    row = (
        db.query(AuthChallenge)
        .filter(
            AuthChallenge.challenge_id == str(challenge_id or ""),
            AuthChallenge.purpose == "login",
        )
        .first()
    )

    if row is None:
        raise _bad_code()

    result = otp.check_attempt(
        submitted=submitted,
        challenge_id=row.challenge_id,
        code_hash=row.code_hash,
        expires_at=row.expires_at,
        attempts=row.attempts,
        consumed_at=row.consumed_at,
        now=_now(),
    )

    if result == "ok" and row.user_id is None:
        result = "wrong"

    if result == "wrong":
        row.attempts += 1
        db.commit()
        left = max(0, otp.OTP_MAX_ATTEMPTS - row.attempts)

        if left == 0:
            raise AuthError(
                429,
                "CODE_LOCKED",
                "Too many incorrect codes. Sign in again to get a new code.",
            )

        raise _bad_code(left)

    if result == "expired":
        raise AuthError(
            400,
            "CODE_EXPIRED",
            "That code has expired. Request a new one.",
        )

    if result == "locked":
        raise AuthError(
            429,
            "CODE_LOCKED",
            "Too many incorrect codes. Sign in again to get a new code.",
        )

    if result == "used":
        raise _bad_code()

    row.consumed_at = _now()
    db.commit()

    return int(row.user_id)


def resend_challenge(
    db: Session,
    challenge_id: str,
) -> tuple[int | None, str | None]:
    """
    Issues a fresh code for an open challenge.

    Returns (user_id, new_code). For a decoy challenge it returns (None, None),
    so nothing is emailed but the caller can answer exactly as for a real one.
    """

    row = (
        db.query(AuthChallenge)
        .filter(
            AuthChallenge.challenge_id == str(challenge_id or ""),
            AuthChallenge.purpose == "login",
        )
        .first()
    )

    if row is None or row.consumed_at is not None:
        raise _bad_code()

    now = _now()

    allowed, wait = otp.resend_allowed(
        last_sent_at=row.last_sent_at,
        resend_count=row.resend_count,
        now=now,
    )

    if not allowed:
        if wait == 0:
            raise AuthError(
                429,
                "RESEND_LIMIT",
                "Too many codes requested. Sign in again to start over.",
            )

        raise AuthError(
            429,
            "RESEND_WAIT",
            f"Please wait {wait} seconds before requesting another code.",
            retry_after=wait,
        )

    code = otp.generate_code()

    row.code_hash = otp.hash_code(code, row.challenge_id)
    row.expires_at = otp.expiry_time(now)
    row.last_sent_at = now
    row.resend_count += 1
    db.commit()

    if row.user_id is None:
        return None, None

    return int(row.user_id), code


def record_login(db: Session, user_id: int) -> tuple[AuthSecurity, bool]:
    """
    Records a completed sign-in. The first correct emailed code also proves
    the person owns the email address.

    Returns (security, send_welcome). The welcome email is only for accounts
    created through the sign-up form (they accepted the terms there), and only
    once: older accounts that never signed up this way do not get one.
    """

    security = get_security(db, user_id)
    now = _now()

    first_verification = security.email_verified_at is None

    if first_verification:
        security.email_verified_at = now

    security.last_login_at = now
    db.commit()

    send_welcome = first_verification and security.terms_accepted_at is not None

    return security, send_welcome


# ------------------------------------------------------------------ #
# Password reset                                                      #
# ------------------------------------------------------------------ #

def create_reset_token(db: Session, user: User, ip: str | None) -> str:
    now = _now()

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).update({PasswordResetToken.used_at: now}, synchronize_session=False)

    raw, hashed = new_token()

    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hashed,
            expires_at=now + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
            created_at=now,
            ip_address=ip,
        )
    )
    db.commit()

    return raw


def _bad_link() -> AuthError:
    return AuthError(
        400,
        "RESET_LINK_INVALID",
        "This reset link is no longer valid. Request a new one.",
    )


def reset_password(db: Session, raw_token: str, new_password: str) -> User:
    if not is_plausible_token(raw_token):
        raise _bad_link()

    row = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == hash_token(raw_token))
        .first()
    )

    now = _now()

    if row is None or row.used_at is not None or row.expires_at <= now:
        raise _bad_link()

    user = db.query(User).filter(User.id == row.user_id).first()

    if user is None or not user.is_active:
        raise _bad_link()

    problems = validate_password(new_password, user.email)

    if problems:
        # The link is NOT used up, so the person can try a better password.
        raise AuthError(422, "WEAK_PASSWORD", " ".join(problems))

    user.password_hash = hash_password(new_password)
    row.used_at = now

    security = get_security(db, user.id)
    security.token_version += 1
    security.password_changed_at = now

    db.query(AuthChallenge).filter(
        AuthChallenge.user_id == user.id,
        AuthChallenge.consumed_at.is_(None),
    ).update({AuthChallenge.consumed_at: now}, synchronize_session=False)

    db.commit()
    db.refresh(user)

    return user


def sign_out_everywhere(db: Session, user_id: int) -> None:
    security = get_security(db, user_id)
    security.token_version += 1
    db.commit()
