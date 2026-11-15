"""
Tables for sign-in security.

* AuthChallenge       one row per emailed login code (only a keyed hash of the
                      code is stored). A row with no user is a decoy that makes
                      "register an email that already exists" look identical.
* PasswordResetToken  one row per reset link (only a hash of the token is stored).
* AuthSecurity        one row per user: the session version (raising it signs the
                      user out everywhere), plus a few audit timestamps.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AuthChallenge(Base):
    __tablename__ = "auth_challenges"

    id = Column(Integer, primary_key=True, index=True)

    challenge_id = Column(String(64), unique=True, index=True, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    purpose = Column(String(30), nullable=False, default="login")
    code_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    resend_count = Column(Integer, nullable=False, default=0)
    last_sent_at = Column(DateTime, nullable=False, default=_now)
    consumed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    ip_address = Column(String(64), nullable=True)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    ip_address = Column(String(64), nullable=True)


class AuthSecurity(Base):
    __tablename__ = "auth_security"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    token_version = Column(Integer, nullable=False, default=0)
    password_changed_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    terms_accepted_at = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
