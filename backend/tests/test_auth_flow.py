"""
End-to-end tests of the secured sign-in: registration, the emailed code,
lockouts, password reset, sign-out-everywhere and owner-only admin.

They run against a throw-away in-memory database and a tiny app that mounts
only the auth routes, so nothing touches your real data.
"""

import importlib
import pkgutil
import re
from datetime import timedelta

import pytest

pytest.importorskip("httpx")

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database.database import Base, get_db
from models.auth_security import AuthChallenge, AuthSecurity, PasswordResetToken
from models.user import User
from services import auth_flow, auth_service
from services.security import otp

PASSWORD = "Correct-Horse-47-Battery"
NEW_PASSWORD = "Another-Strong-Pass-91"


def _load_all_models():
    for info in pkgutil.iter_modules(models.__path__):
        name = info.name

        if "." in name or "before" in name or "backup" in name:
            continue

        try:
            importlib.import_module(f"models.{name}")
        except Exception:
            pass


_load_all_models()

import routes.v1.auth as auth_routes  # noqa: E402
from dependencies.admin import require_admin  # noqa: E402
from services.dependencies import get_current_user  # noqa: E402


@pytest.fixture(autouse=True)
def fast_hashing():
    # 600,000 rounds is right for production and slow for tests.
    original = auth_service.pwd_context
    auth_service.pwd_context = auth_service.CryptContext(
        schemes=["pbkdf2_sha256"],
        deprecated="auto",
        pbkdf2_sha256__default_rounds=1000,
        pbkdf2_sha256__min_rounds=1000,
    )
    auth_service._dummy_hash = None
    yield
    auth_service.pwd_context = original
    auth_service._dummy_hash = None


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:5173")
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("OWNER_EMAIL", raising=False)
    monkeypatch.delenv("TRUST_PROXY", raising=False)


@pytest.fixture
def mails(monkeypatch):
    sent = []
    monkeypatch.setattr(auth_routes, "send_email_safely", lambda mail: sent.append(mail) or True)
    return sent


@pytest.fixture
def db_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            AuthChallenge.__table__,
            PasswordResetToken.__table__,
            AuthSecurity.__table__,
        ],
    )
    return sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def client(db_factory, env, mails):
    app = FastAPI()
    app.include_router(auth_routes.router, prefix="/api/v1")

    @app.get("/admin-only")
    def admin_only(user: User = Depends(require_admin)):
        return {"ok": user.email}

    @app.get("/private")
    def private(user: User = Depends(get_current_user)):
        return {"email": user.email}

    def override():
        session = db_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    auth_routes.reset_limiters()

    test_client = TestClient(app)
    test_client.db_factory = db_factory
    yield test_client
    auth_routes.reset_limiters()


def code_from(mail) -> str:
    return re.search(r"login code is: (\d{6})", mail.text).group(1)


def link_token_from(mail) -> str:
    return re.search(r"reset=([A-Za-z0-9_-]+)", mail.text).group(1)


def register(client, email="Neliswa@Example.com", password=PASSWORD, **extra):
    body = {"email": email, "password": password, "full_name": "Neliswa M", "accept_terms": True}
    body.update(extra)
    return client.post("/api/v1/auth/register", json=body)


def login_step(client, email="neliswa@example.com", password=PASSWORD):
    return client.post("/api/v1/auth/login", data={"username": email, "password": password})


def sign_in(client, mails, email="neliswa@example.com", password=PASSWORD):
    response = login_step(client, email, password)
    assert response.status_code == 200, response.text
    code = code_from(mails[-1])
    verified = client.post(
        "/api/v1/auth/login/verify",
        json={"challenge_id": response.json()["challenge_id"], "code": code},
    )
    assert verified.status_code == 200, verified.text
    return verified.json()["access_token"]


def make_user(client, email="neliswa@example.com", password=PASSWORD, **fields):
    with client.db_factory() as db:
        user = User(email=email, password_hash=auth_service.hash_password(password), **fields)
        db.add(user)
        db.commit()
        return user.id


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------- registration

def test_registration_creates_the_account_and_sends_only_the_code(client, mails):
    response = register(client)

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "otp_required"
    assert body["email_hint"] == "n***@example.com"
    assert len(body["challenge_id"]) >= 40
    assert "access_token" not in body

    # nothing but the code goes out until the address is proved
    assert [m.subject for m in mails] == ["Your TradePilot AI login code"]
    assert all(m.to == "neliswa@example.com" for m in mails)

    with client.db_factory() as db:
        user = db.query(User).one()
        assert user.email == "neliswa@example.com"
        assert user.full_name == "Neliswa M"
        assert user.password_hash != PASSWORD and user.password_hash.startswith("$pbkdf2-sha256$")
        security = db.query(AuthSecurity).one()
        assert security.terms_accepted_at is not None
        assert security.email_verified_at is None


def test_the_welcome_email_arrives_once_the_address_is_proved(client, mails):
    first = register(client).json()
    assert [m.subject for m in mails] == ["Your TradePilot AI login code"]

    verified = client.post(
        "/api/v1/auth/login/verify",
        json={"challenge_id": first["challenge_id"], "code": code_from(mails[-1])},
    )
    assert verified.status_code == 200

    assert [m.subject for m in mails] == ["Your TradePilot AI login code", "Welcome to TradePilot AI"]
    assert "http://localhost:5173/login" in mails[-1].text

    with client.db_factory() as db:
        assert db.query(AuthSecurity).one().email_verified_at is not None

    # a later sign-in does not repeat the welcome
    mails.clear()
    sign_in(client, mails)
    assert [m.subject for m in mails] == ["Your TradePilot AI login code"]


def test_accounts_that_existed_before_sign_up_verification_get_no_welcome(client, mails):
    make_user(client)
    sign_in(client, mails)
    assert [m.subject for m in mails] == ["Your TradePilot AI login code"]

    with client.db_factory() as db:
        security = db.query(AuthSecurity).one()
        assert security.email_verified_at is not None and security.terms_accepted_at is None


def test_weak_passwords_and_missing_terms_are_refused(client, mails):
    weak = register(client, password="password123")
    assert weak.status_code == 422 and weak.json()["detail"]["code"] == "WEAK_PASSWORD"

    short = register(client, password="Ab1!")
    assert short.status_code == 422

    no_terms = register(client, accept_terms=False)
    assert no_terms.status_code == 422 and no_terms.json()["detail"]["code"] == "TERMS_REQUIRED"

    assert mails == []
    with client.db_factory() as db:
        assert db.query(User).count() == 0


def test_registering_an_existing_email_looks_identical_and_warns_the_owner(client, mails):
    register(client)
    mails.clear()

    again = register(client, password=NEW_PASSWORD)

    assert again.status_code == 202
    assert set(again.json()) == {"status", "challenge_id", "email_hint", "expires_in", "resend_in"}
    assert [m.subject for m in mails] == ["Someone tried to register your TradePilot AI email"]
    assert "login code" not in mails[0].text

    with client.db_factory() as db:
        assert db.query(User).count() == 1
        # the original password still works; the stranger's did not replace it
        user = db.query(User).one()
        assert auth_service.verify_password(PASSWORD, user.password_hash)


def test_a_decoy_code_can_never_sign_anyone_in(client, mails):
    register(client)
    decoy = register(client).json()

    for guess in ["000000", "123456", "999999", "111111", "222222"]:
        response = client.post("/api/v1/auth/login/verify", json={"challenge_id": decoy["challenge_id"], "code": guess})
        assert response.status_code in (400, 429)
        assert "access_token" not in response.text

    locked = client.post("/api/v1/auth/login/verify", json={"challenge_id": decoy["challenge_id"], "code": "123456"})
    assert locked.status_code == 429


def test_the_decoy_resend_answers_like_a_real_one_but_sends_nothing(client, mails):
    register(client)
    decoy = register(client).json()
    mails.clear()

    with client.db_factory() as db:
        row = db.query(AuthChallenge).filter(AuthChallenge.challenge_id == decoy["challenge_id"]).one()
        row.last_sent_at = row.last_sent_at - timedelta(minutes=5)
        db.commit()

    response = client.post("/api/v1/auth/login/resend", json={"challenge_id": decoy["challenge_id"]})
    assert response.status_code == 200 and response.json() == {"resend_in": 60}
    assert mails == []


def test_names_are_cleaned(client, mails):
    register(client, full_name="  Nel\x00iswa   <b>M</b>\n ")
    with client.db_factory() as db:
        assert db.query(User).one().full_name == "Neliswa <b>M</b>"


# ----------------------------------------------------------------- the code step

def test_a_correct_password_gets_a_code_not_a_token(client, mails):
    make_user(client, full_name="Neliswa")

    response = login_step(client)

    assert response.status_code == 200
    assert response.json()["status"] == "otp_required"
    assert "access_token" not in response.text
    assert len(mails) == 1 and "482" not in mails[0].subject
    assert re.fullmatch(r"\d{6}", code_from(mails[0]))


def test_the_right_code_signs_in_and_the_token_works(client, mails):
    make_user(client)
    token = sign_in(client, mails)

    assert client.get("/private", headers=auth_header(token)).json() == {"email": "neliswa@example.com"}
    assert client.get("/api/v1/auth/me", headers=auth_header(token)).json()["email"] == "neliswa@example.com"

    with client.db_factory() as db:
        assert db.query(AuthSecurity).one().last_login_at is not None


def test_a_code_works_once_only(client, mails):
    make_user(client)
    challenge = login_step(client).json()
    code = code_from(mails[-1])
    body = {"challenge_id": challenge["challenge_id"], "code": code}

    assert client.post("/api/v1/auth/login/verify", json=body).status_code == 200
    replay = client.post("/api/v1/auth/login/verify", json=body)
    assert replay.status_code == 400 and replay.json()["detail"]["code"] == "CODE_INVALID"


def test_wrong_codes_are_counted_and_then_locked(client, mails):
    make_user(client)
    challenge = login_step(client).json()
    real = code_from(mails[-1])
    wrong = "000000" if real != "000000" else "111111"
    body = {"challenge_id": challenge["challenge_id"], "code": wrong}

    for expected_left in (4, 3, 2, 1):
        response = client.post("/api/v1/auth/login/verify", json=body)
        assert response.status_code == 400
        assert response.json()["detail"]["attempts_left"] == expected_left

    fifth = client.post("/api/v1/auth/login/verify", json=body)
    assert fifth.status_code == 429 and fifth.json()["detail"]["code"] == "CODE_LOCKED"
    assert "Retry-After" in fifth.headers

    # even the correct code is refused once locked
    final = client.post("/api/v1/auth/login/verify", json={"challenge_id": challenge["challenge_id"], "code": real})
    assert final.status_code == 429


def test_an_expired_code_is_refused(client, mails):
    make_user(client)
    challenge = login_step(client).json()
    code = code_from(mails[-1])

    with client.db_factory() as db:
        row = db.query(AuthChallenge).one()
        row.expires_at = otp.utc_now() - timedelta(seconds=1)
        db.commit()

    response = client.post("/api/v1/auth/login/verify", json={"challenge_id": challenge["challenge_id"], "code": code})
    assert response.status_code == 400 and response.json()["detail"]["code"] == "CODE_EXPIRED"


def test_unknown_challenges_and_malformed_requests_are_refused(client):
    bogus = client.post("/api/v1/auth/login/verify", json={"challenge_id": "x" * 43, "code": "123456"})
    assert bogus.status_code == 400 and bogus.json()["detail"]["code"] == "CODE_INVALID"
    assert client.post("/api/v1/auth/login/verify", json={"challenge_id": "short", "code": "1"}).status_code == 422
    assert client.post("/api/v1/auth/login/verify", json={}).status_code == 422


def test_a_code_from_one_sign_in_does_not_work_for_another(client, mails):
    make_user(client)
    first = login_step(client).json()
    first_code = code_from(mails[-1])
    second = login_step(client).json()

    response = client.post("/api/v1/auth/login/verify", json={"challenge_id": second["challenge_id"], "code": first_code})
    assert response.status_code in (200, 400)  # 200 only on a 1-in-a-million collision
    assert first["challenge_id"] != second["challenge_id"]


def test_resend_has_a_cooldown_and_a_limit_and_replaces_the_old_code(client, mails):
    make_user(client)
    challenge = login_step(client).json()
    old_code = code_from(mails[-1])
    body = {"challenge_id": challenge["challenge_id"]}

    too_soon = client.post("/api/v1/auth/login/resend", json=body)
    assert too_soon.status_code == 429 and too_soon.json()["detail"]["code"] == "RESEND_WAIT"
    assert 1 <= too_soon.json()["detail"]["retry_after"] <= 60

    def age_the_last_send():
        with client.db_factory() as db:
            row = db.query(AuthChallenge).one()
            row.last_sent_at = row.last_sent_at - timedelta(seconds=90)
            db.commit()

    age_the_last_send()
    ok = client.post("/api/v1/auth/login/resend", json=body)
    assert ok.status_code == 200 and ok.json() == {"resend_in": 60}
    new_code = code_from(mails[-1])
    assert len(mails) == 2

    if new_code != old_code:
        stale = client.post("/api/v1/auth/login/verify", json={**body, "code": old_code})
        assert stale.status_code == 400

    for _ in range(2):
        age_the_last_send()
        assert client.post("/api/v1/auth/login/resend", json=body).status_code == 200

    age_the_last_send()
    capped = client.post("/api/v1/auth/login/resend", json=body)
    assert capped.status_code == 429 and capped.json()["detail"]["code"] == "RESEND_LIMIT"


# ------------------------------------------------------------ passwords and lockouts

def test_wrong_password_and_unknown_email_give_the_same_answer(client, mails):
    make_user(client)

    wrong = login_step(client, password="Not-The-Password-1")
    unknown = login_step(client, email="nobody@example.com")

    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert mails == []


def test_unknown_emails_burn_the_same_time_as_real_ones(client, monkeypatch):
    calls = []
    monkeypatch.setattr(auth_flow, "burn_password_time", lambda password: calls.append(password))

    login_step(client, email="nobody@example.com")

    assert calls == [PASSWORD]


def test_five_wrong_passwords_lock_the_email_for_known_and_unknown_accounts(client, mails):
    make_user(client)

    for email in ("neliswa@example.com", "ghost@example.com"):
        for _ in range(5):
            assert login_step(client, email=email, password="Wrong-Password-1").status_code == 401

        blocked = login_step(client, email=email, password=PASSWORD)
        assert blocked.status_code == 429
        assert blocked.json()["detail"]["code"] == "TOO_MANY_ATTEMPTS"
        assert "Retry-After" in blocked.headers

    assert mails == []


def test_a_successful_password_clears_earlier_failures(client, mails):
    make_user(client)

    for _ in range(4):
        login_step(client, password="Wrong-Password-1")

    assert login_step(client).status_code == 200

    for _ in range(4):
        assert login_step(client, password="Wrong-Password-1").status_code == 401


def test_the_address_limit_stops_a_flood_of_different_emails(client, monkeypatch):
    monkeypatch.setattr(auth_routes, "login_ip", auth_routes.SlidingWindowLimiter(3, 300))

    codes = [login_step(client, email=f"user{i}@example.com").status_code for i in range(5)]
    assert codes[:3] == [401, 401, 401] and codes[3:] == [429, 429]


def test_oversized_passwords_are_not_hashed(client, monkeypatch):
    make_user(client)
    result = login_step(client, password="x" * 5000)
    assert result.status_code == 401


def test_a_suspended_account_cannot_get_a_code(client, mails):
    make_user(client, is_active=False)
    response = login_step(client)
    assert response.status_code == 403 and response.json()["detail"]["code"] == "ACCOUNT_INACTIVE"
    assert mails == []


def test_a_suspended_account_loses_access_with_an_existing_token(client, mails):
    user_id = make_user(client)
    token = sign_in(client, mails)

    with client.db_factory() as db:
        db.query(User).filter(User.id == user_id).one().is_active = False
        db.commit()

    response = client.get("/private", headers=auth_header(token))
    assert response.status_code == 403 and response.json()["detail"]["code"] == "ACCOUNT_INACTIVE"


def test_old_password_hashes_are_upgraded_at_the_next_sign_in(client, mails):
    weak = auth_service.CryptContext(schemes=["pbkdf2_sha256"], pbkdf2_sha256__default_rounds=500).hash(PASSWORD)
    make_user(client)
    with client.db_factory() as db:
        db.query(User).one().password_hash = weak
        db.commit()

    assert login_step(client).status_code == 200

    with client.db_factory() as db:
        stored = db.query(User).one().password_hash
        assert stored != weak and "$1000$" in stored


# --------------------------------------------------------------------- tokens

def test_tokens_from_the_old_system_or_forged_ones_are_refused(client):
    from jose import jwt as jose_jwt

    from config.security import ALGORITHM, SECRET_KEY

    make_user(client)

    no_version = jose_jwt.encode({"sub": "x", "id": 1}, SECRET_KEY, algorithm=ALGORITHM)
    wrong_key = jose_jwt.encode({"sub": "x", "id": 1, "tv": 0}, "another-secret-key-" + "z" * 40, algorithm=ALGORITHM)
    wrong_type = jose_jwt.encode({"sub": "x", "id": "1", "tv": 0}, SECRET_KEY, algorithm=ALGORITHM)

    for token in (no_version, wrong_key, wrong_type, "garbage", ""):
        response = client.get("/private", headers=auth_header(token))
        assert response.status_code == 401

    assert client.get("/private").status_code == 401


def test_the_none_algorithm_trick_does_not_work(client):
    import base64
    import json

    def part(data):
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()

    make_user(client)
    forged = part({"alg": "none", "typ": "JWT"}) + "." + part({"sub": "x", "id": 1, "tv": 0}) + "."
    assert client.get("/private", headers=auth_header(forged)).status_code == 401


def test_sign_out_everywhere_ends_every_session(client, mails):
    make_user(client)
    first = sign_in(client, mails)
    second = sign_in(client, mails)

    assert client.get("/private", headers=auth_header(first)).status_code == 200
    assert client.post("/api/v1/auth/logout-all", headers=auth_header(first)).status_code == 200

    assert client.get("/private", headers=auth_header(first)).status_code == 401
    assert client.get("/private", headers=auth_header(second)).status_code == 401


# --------------------------------------------------------------- password reset

def test_forgot_password_gives_the_same_answer_for_everyone(client, mails):
    make_user(client)

    known = client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    unknown = client.post("/api/v1/auth/password/forgot", json={"email": "ghost@example.com"})

    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()
    assert len(mails) == 1 and mails[0].to == "neliswa@example.com"
    assert "http://localhost:5173/login?reset=" in mails[0].text


def test_a_reset_link_is_stored_hashed_and_works_once(client, mails):
    make_user(client)
    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    raw = link_token_from(mails[-1])

    with client.db_factory() as db:
        stored = db.query(PasswordResetToken).one()
        assert stored.token_hash != raw and raw not in stored.token_hash

    done = client.post("/api/v1/auth/password/reset", json={"token": raw, "new_password": NEW_PASSWORD})
    assert done.status_code == 200
    assert mails[-1].subject == "Your TradePilot AI password was changed"

    again = client.post("/api/v1/auth/password/reset", json={"token": raw, "new_password": NEW_PASSWORD + "x"})
    assert again.status_code == 400 and again.json()["detail"]["code"] == "RESET_LINK_INVALID"

    assert login_step(client, password=PASSWORD).status_code == 401
    assert login_step(client, password=NEW_PASSWORD).status_code == 200


def test_a_weak_new_password_does_not_use_up_the_link(client, mails):
    make_user(client)
    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    raw = link_token_from(mails[-1])

    weak = client.post("/api/v1/auth/password/reset", json={"token": raw, "new_password": "password123"})
    assert weak.status_code == 422 and weak.json()["detail"]["code"] == "WEAK_PASSWORD"

    assert client.post("/api/v1/auth/password/reset", json={"token": raw, "new_password": NEW_PASSWORD}).status_code == 200


def test_expired_wrong_and_malformed_links_are_refused(client, mails):
    make_user(client)
    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    raw = link_token_from(mails[-1])

    with client.db_factory() as db:
        db.query(PasswordResetToken).one().expires_at = otp.utc_now() - timedelta(seconds=1)
        db.commit()

    for token in (raw, "A" * 43, "short" * 5):
        response = client.post("/api/v1/auth/password/reset", json={"token": token, "new_password": NEW_PASSWORD})
        assert response.status_code == 400 and response.json()["detail"]["code"] == "RESET_LINK_INVALID"


def test_a_new_reset_request_cancels_the_older_link(client, mails):
    make_user(client)
    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    first = link_token_from(mails[-1])
    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    second = link_token_from(mails[-1])

    assert first != second
    assert client.post("/api/v1/auth/password/reset", json={"token": first, "new_password": NEW_PASSWORD}).status_code == 400
    assert client.post("/api/v1/auth/password/reset", json={"token": second, "new_password": NEW_PASSWORD}).status_code == 200


def test_resetting_the_password_signs_out_every_session_and_cancels_pending_codes(client, mails):
    make_user(client)
    token = sign_in(client, mails)
    pending = login_step(client).json()
    pending_code = code_from(mails[-1])

    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    raw = link_token_from(mails[-1])
    client.post("/api/v1/auth/password/reset", json={"token": raw, "new_password": NEW_PASSWORD})

    assert client.get("/private", headers=auth_header(token)).status_code == 401
    used = client.post("/api/v1/auth/login/verify", json={"challenge_id": pending["challenge_id"], "code": pending_code})
    assert used.status_code == 400


def test_forgot_password_is_rate_limited_per_email_without_telling_anyone(client, mails):
    make_user(client)

    answers = [client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"}) for _ in range(5)]

    assert {a.status_code for a in answers} == {202}
    assert len(mails) == 3


def test_a_suspended_account_gets_no_reset_email(client, mails):
    make_user(client, is_active=False)
    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    assert mails == []


# ---------------------------------------------------------------- owner-only admin

def test_admin_in_development_accepts_any_admin_unless_an_owner_is_named(client, mails, monkeypatch):
    make_user(client, is_admin=True)
    make_user(client, email="other@example.com", is_admin=True)
    owner = sign_in(client, mails)
    other = sign_in(client, mails, email="other@example.com")

    assert client.get("/admin-only", headers=auth_header(owner)).status_code == 200
    assert client.get("/admin-only", headers=auth_header(other)).status_code == 200

    monkeypatch.setenv("OWNER_EMAIL", "Neliswa@Example.com")
    assert client.get("/admin-only", headers=auth_header(owner)).status_code == 200
    assert client.get("/admin-only", headers=auth_header(other)).status_code == 403


def test_admin_in_production_fails_closed_without_an_owner(client, mails, monkeypatch):
    make_user(client, is_admin=True)
    token = sign_in(client, mails)
    monkeypatch.setenv("APP_ENV", "production")

    assert client.get("/admin-only", headers=auth_header(token)).status_code == 403

    monkeypatch.setenv("OWNER_EMAIL", "neliswa@example.com")
    assert client.get("/admin-only", headers=auth_header(token)).status_code == 200


def test_being_the_owner_is_not_enough_without_the_admin_flag(client, mails, monkeypatch):
    make_user(client, is_admin=False)
    token = sign_in(client, mails)
    monkeypatch.setenv("OWNER_EMAIL", "neliswa@example.com")
    assert client.get("/admin-only", headers=auth_header(token)).status_code == 403


# -------------------------------------------------------------------- settings

def test_production_links_must_be_https(client, mails, monkeypatch):
    make_user(client)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("FRONTEND_URL", "http://insecure.example.com")

    with pytest.raises(RuntimeError):
        client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})


def test_the_forwarded_address_is_only_trusted_behind_a_proxy(client, monkeypatch):
    monkeypatch.setattr(auth_routes, "login_ip", auth_routes.SlidingWindowLimiter(1, 300))
    headers_a = {"X-Forwarded-For": "1.1.1.1"}
    headers_b = {"X-Forwarded-For": "2.2.2.2"}

    # not trusted: both look like the same caller, so the second is limited
    first = client.post("/api/v1/auth/login", data={"username": "a@example.com", "password": "x"}, headers=headers_a)
    second = client.post("/api/v1/auth/login", data={"username": "b@example.com", "password": "x"}, headers=headers_b)
    assert (first.status_code, second.status_code) == (401, 429)

    monkeypatch.setenv("TRUST_PROXY", "true")
    auth_routes.reset_limiters()
    monkeypatch.setattr(auth_routes, "login_ip", auth_routes.SlidingWindowLimiter(1, 300))
    first = client.post("/api/v1/auth/login", data={"username": "a@example.com", "password": "x"}, headers=headers_a)
    second = client.post("/api/v1/auth/login", data={"username": "b@example.com", "password": "x"}, headers=headers_b)
    assert (first.status_code, second.status_code) == (401, 401)
