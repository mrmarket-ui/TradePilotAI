"""
Sign-in routes.

Signing in is two steps: the password, then a one-time code sent by email.
A login token is only ever issued after the code is verified. Accounts can be
registered, passwords reset by email link, and every session ended at once.
"""

import os
import secrets
from datetime import timedelta

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User
from schemas.user import UserCreate

from services import auth_flow
from services.auth_flow import AuthError
from services import notifications
from services.auth_service import hash_password
from services.dependencies import get_current_user
from services.jwt_service import create_access_token
from services.mailer import templates
from services.mailer.sender import send_email_safely
from services.security import otp
from services.security.password_policy import validate_password
from services.security.rate_limit import SlidingWindowLimiter
from services.security.tokens import RESET_TOKEN_TTL_MINUTES

router = APIRouter()


# ------------------------------------------------------------------ #
# Rate limits (per server process)                                    #
# ------------------------------------------------------------------ #

login_ip = SlidingWindowLimiter(30, 300)
login_failures = SlidingWindowLimiter(5, 900)
register_ip = SlidingWindowLimiter(10, 3600)
verify_ip = SlidingWindowLimiter(40, 300)
resend_ip = SlidingWindowLimiter(10, 600)
forgot_ip = SlidingWindowLimiter(10, 3600)
forgot_email = SlidingWindowLimiter(3, 3600)
reset_ip = SlidingWindowLimiter(20, 3600)

_LIMITERS = (
    login_ip,
    login_failures,
    register_ip,
    verify_ip,
    resend_ip,
    forgot_ip,
    forgot_email,
    reset_ip,
)


def reset_limiters() -> None:
    for limiter in _LIMITERS:
        limiter.clear()


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def client_ip(request: Request) -> str:
    """The caller's address. Only trust X-Forwarded-For when TRUST_PROXY=true,
    which is right behind a proxy that sets it (and wrong otherwise)."""

    if os.getenv("TRUST_PROXY", "").strip().lower() == "true":
        forwarded = request.headers.get("x-forwarded-for", "")

        if forwarded:
            return forwarded.split(",")[0].strip()[:64]

    return (request.client.host if request.client else "unknown")[:64]


def _limit(limiter: SlidingWindowLimiter, key: str) -> None:
    if not limiter.allow(key):
        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMITED",
                "message": "Too many requests. Please wait a few minutes and try again.",
            },
            headers={"Retry-After": str(limiter.retry_after(key))},
        )


def _http(error: AuthError) -> HTTPException:
    headers = None

    if error.status_code == 429:
        headers = {"Retry-After": str(error.extra.get("retry_after") or 60)}

    return HTTPException(
        status_code=error.status_code,
        detail=error.detail(),
        headers=headers,
    )


def frontend_url() -> str:
    url = os.getenv("FRONTEND_URL", "http://localhost:5173").strip().rstrip("/")

    production = os.getenv("APP_ENV", "development").strip().lower() == "production"

    if production and not url.startswith("https://"):
        raise RuntimeError("FRONTEND_URL must start with https:// in production.")

    return url


def _challenge_payload(challenge, email: str) -> dict:
    return {
        "status": "otp_required",
        "challenge_id": challenge.challenge_id,
        "email_hint": otp.mask_email(email),
        "expires_in": otp.OTP_TTL_MINUTES * 60,
        "resend_in": otp.OTP_RESEND_COOLDOWN_SECONDS,
    }


def _send_code(background: BackgroundTasks, user: User, code: str) -> None:
    background.add_task(
        send_email_safely,
        templates.login_code_mail(
            to=user.email,
            full_name=user.full_name,
            code=code,
            minutes=otp.OTP_TTL_MINUTES,
        ),
    )


# ------------------------------------------------------------------ #
# Request bodies                                                      #
# ------------------------------------------------------------------ #

class CodeBody(BaseModel):
    challenge_id: str = Field(min_length=20, max_length=64)
    code: str = Field(min_length=1, max_length=16)


class ResendBody(BaseModel):
    challenge_id: str = Field(min_length=20, max_length=64)


class ForgotBody(BaseModel):
    email: EmailStr


class ResetBody(BaseModel):
    token: str = Field(min_length=20, max_length=128)
    new_password: str = Field(min_length=1, max_length=256)


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@router.post("/auth/register", status_code=202)
def register(
    payload: UserCreate,
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    ip = client_ip(request)
    _limit(register_ip, ip)

    email = auth_flow.normalise_email(payload.email)

    problems = validate_password(payload.password, email)

    if problems:
        raise HTTPException(
            status_code=422,
            detail={"code": "WEAK_PASSWORD", "message": " ".join(problems)},
        )

    if not payload.accept_terms:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "TERMS_REQUIRED",
                "message": "Please accept the Terms & Privacy Policy to create your account.",
            },
        )

    # Hash first, in every case, so the response time does not reveal
    # whether the email already has an account.
    password_hash = hash_password(payload.password)

    user = auth_flow.register_user(
        db,
        email=email,
        password_hash=password_hash,
        full_name=auth_flow.clean_name(payload.full_name),
    )

    if user is None:
        existing = auth_flow.find_user(db, email)
        challenge, _unused = auth_flow.start_challenge(db, None, ip)

        if existing is not None and existing.is_active:
            background.add_task(
                send_email_safely,
                templates.existing_account_mail(
                    to=existing.email,
                    full_name=existing.full_name,
                    login_url=frontend_url() + "/login",
                ),
            )
    else:
        challenge, code = auth_flow.start_challenge(db, user.id, ip)

        # The welcome email follows once the person proves they own this
        # address by entering the code (see verify_login).
        _send_code(background, user, code)

    return _challenge_payload(challenge, email)


@router.post("/auth/login")
def login(
    request: Request,
    background: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    ip = client_ip(request)
    _limit(login_ip, ip)

    email = auth_flow.normalise_email(form_data.username)

    if login_failures.blocked(email):
        raise HTTPException(
            status_code=429,
            detail={
                "code": "TOO_MANY_ATTEMPTS",
                "message": "Too many failed attempts. Please wait a few minutes or reset your password.",
            },
            headers={"Retry-After": str(login_failures.retry_after(email))},
        )

    try:
        user = auth_flow.authenticate(db, email, form_data.password)
    except AuthError as error:
        if error.code == "INVALID_CREDENTIALS":
            login_failures.add(email)

        raise _http(error) from None

    login_failures.clear(email)

    challenge, code = auth_flow.start_challenge(db, user.id, ip)
    _send_code(background, user, code)

    return _challenge_payload(challenge, user.email)


@router.post("/auth/login/verify")
def verify_login(
    body: CodeBody,
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    ip = client_ip(request)
    _limit(verify_ip, ip)

    try:
        user_id = auth_flow.verify_challenge(db, body.challenge_id, body.code)
    except AuthError as error:
        raise _http(error) from None

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ACCOUNT_INACTIVE",
                "message": "This account has been suspended or deactivated.",
            },
        )

    security, send_welcome = auth_flow.record_login(db, user.id)

    if send_welcome:
        background.add_task(
            send_email_safely,
            templates.welcome_mail(
                to=user.email,
                full_name=user.full_name,
                app_url=frontend_url() + "/login",
            ),
        )
        notifications.notify_safely(
            db,
            user.id,
            "account.welcome",
            "Welcome to TradePilot AI",
            "Your account is ready. Start by logging a trade or exploring Macro Intelligence.",
            link="/dashboard",
            severity="success",
        )

    # A security alert for every new sign-in (repeats from the same address
    # within a day are not shown again).
    notifications.notify_safely(
        db,
        user.id,
        "security.signin",
        "New sign-in to your account",
        f"A sign-in was completed from IP address {ip}. "
        "If this was not you, reset your password right away.",
        link="/settings",
        severity="security",
        dedupe_within=timedelta(hours=24),
    )

    token = create_access_token(
        data={
            "sub": user.email,
            "id": user.id,
            "tv": security.token_version,
            "jti": secrets.token_urlsafe(8),
        }
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/login/resend")
def resend_login_code(
    body: ResendBody,
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    _limit(resend_ip, client_ip(request))

    try:
        user_id, code = auth_flow.resend_challenge(db, body.challenge_id)
    except AuthError as error:
        raise _http(error) from None

    if user_id is not None and code is not None:
        user = db.query(User).filter(User.id == user_id).first()

        if user is not None and user.is_active:
            _send_code(background, user, code)

    return {"resend_in": otp.OTP_RESEND_COOLDOWN_SECONDS}


@router.post("/auth/password/forgot", status_code=202)
def forgot_password(
    body: ForgotBody,
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    ip = client_ip(request)
    _limit(forgot_ip, ip)

    email = auth_flow.normalise_email(body.email)

    # Same answer every time, so this cannot be used to find out who has an account.
    if forgot_email.allow(email):
        user = auth_flow.find_user(db, email)

        if user is not None and user.is_active:
            raw = auth_flow.create_reset_token(db, user, ip)

            background.add_task(
                send_email_safely,
                templates.password_reset_mail(
                    to=user.email,
                    full_name=user.full_name,
                    link=f"{frontend_url()}/login?reset={raw}",
                    minutes=RESET_TOKEN_TTL_MINUTES,
                ),
            )

    return {
        "message": "If an account exists for that email, a reset link has been sent."
    }


@router.post("/auth/password/reset")
def reset_password(
    body: ResetBody,
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    _limit(reset_ip, client_ip(request))

    try:
        user = auth_flow.reset_password(db, body.token, body.new_password)
    except AuthError as error:
        raise _http(error) from None

    background.add_task(
        send_email_safely,
        templates.password_changed_mail(to=user.email, full_name=user.full_name),
    )
    notifications.notify_safely(
        db,
        user.id,
        "security.password_changed",
        "Your password was changed",
        "You were signed out everywhere. If this was not you, reset your password again and contact support.",
        link="/settings",
        severity="security",
    )

    return {"message": "Password updated. Please sign in again."}


@router.post("/auth/logout-all")
def logout_everywhere(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_flow.sign_out_everywhere(db, current_user.id)
    notifications.notify_safely(
        db,
        current_user.id,
        "security.signed_out_everywhere",
        "You signed out of every device",
        "Every active session was ended. Sign in again to continue.",
        link="/settings",
        severity="security",
    )

    return {"message": "You were signed out everywhere."}


@router.get("/auth/me")
def me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "avatar": current_user.avatar,
        "bio": current_user.bio,
        "plan": current_user.plan,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "ai_credits": current_user.ai_credits,
        "preferred_language": current_user.preferred_language,
        "preferred_currency": current_user.preferred_currency,
        "created_at": current_user.created_at,
    }
