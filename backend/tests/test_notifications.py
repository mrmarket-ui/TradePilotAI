"""
Notifications: who can see what, what the bell shows, and the real security
alerts that sign-in now creates. Runs on a throw-away in-memory database.
"""

import importlib
import pkgutil
import re
from datetime import timedelta

import pytest

pytest.importorskip("httpx")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database.database import Base, get_db
from models.auth_security import AuthChallenge, AuthSecurity, PasswordResetToken
from models.notification import Notification
from models.user import User
from services import auth_service
from services import notifications as service

PASSWORD = "Correct-Horse-47-Battery"


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
import routes.v1.notifications as notification_routes  # noqa: E402


@pytest.fixture(autouse=True)
def fast_hashing():
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
def mails(monkeypatch):
    sent = []
    monkeypatch.setattr(auth_routes, "send_email_safely", lambda mail: sent.append(mail) or True)
    return sent


@pytest.fixture
def client(monkeypatch, mails):
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:5173")
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("OWNER_EMAIL", raising=False)

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            AuthChallenge.__table__,
            PasswordResetToken.__table__,
            AuthSecurity.__table__,
            Notification.__table__,
        ],
    )
    factory = sessionmaker(bind=engine, autoflush=False)

    app = FastAPI()
    app.include_router(auth_routes.router, prefix="/api/v1")
    app.include_router(notification_routes.router, prefix="/api/v1")

    def override():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    auth_routes.reset_limiters()

    test_client = TestClient(app)
    test_client.db_factory = factory
    yield test_client
    auth_routes.reset_limiters()


def make_user(client, email="neliswa@example.com", **fields):
    with client.db_factory() as db:
        user = User(email=email, password_hash=auth_service.hash_password(PASSWORD), **fields)
        db.add(user)
        db.commit()
        return user.id


def sign_in(client, mails, email="neliswa@example.com"):
    challenge = client.post("/api/v1/auth/login", data={"username": email, "password": PASSWORD}).json()
    code = re.search(r"login code is: (\d{6})", mails[-1].text).group(1)
    response = client.post(
        "/api/v1/auth/login/verify",
        json={"challenge_id": challenge["challenge_id"], "code": code},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def add(client, user_id, **fields):
    data = dict(type="test", title="Hello", severity="info")
    data.update(fields)
    with client.db_factory() as db:
        return service.notify(db, user_id, **data).id


# ----------------------------------------------------------------- the bell

def test_sign_in_creates_a_real_security_alert(client, mails):
    make_user(client)
    headers = sign_in(client, mails)

    body = client.get("/api/v1/notifications", headers=headers).json()
    assert body["unread"] == 1
    item = body["items"][0]
    assert item["type"] == "security.signin" and item["severity"] == "security"
    assert item["title"] == "New sign-in to your account"
    assert "testclient" in item["body"] or "IP address" in item["body"]
    assert item["read"] is False and item["link"] == "/settings"


def test_the_same_address_does_not_repeat_the_alert_within_a_day(client, mails):
    make_user(client)
    sign_in(client, mails)
    headers = sign_in(client, mails)

    items = client.get("/api/v1/notifications", headers=headers).json()["items"]
    assert [i["type"] for i in items].count("security.signin") == 1


def test_a_new_account_gets_a_welcome_notification_once(client, mails):
    challenge = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": PASSWORD, "full_name": "Neliswa", "accept_terms": True},
    ).json()
    code = re.search(r"login code is: (\d{6})", mails[-1].text).group(1)
    token = client.post(
        "/api/v1/auth/login/verify", json={"challenge_id": challenge["challenge_id"], "code": code}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    types = [i["type"] for i in client.get("/api/v1/notifications", headers=headers).json()["items"]]
    assert sorted(types) == ["account.welcome", "security.signin"]

    again = sign_in(client, mails, email="new@example.com")
    types = [i["type"] for i in client.get("/api/v1/notifications", headers=again).json()["items"]]
    assert types.count("account.welcome") == 1


def test_changing_the_password_and_signing_out_everywhere_are_recorded(client, mails):
    make_user(client)
    headers = sign_in(client, mails)

    assert client.post("/api/v1/auth/logout-all", headers=headers).status_code == 200
    again = sign_in(client, mails)
    types = [i["type"] for i in client.get("/api/v1/notifications", headers=again).json()["items"]]
    assert "security.signed_out_everywhere" in types

    client.post("/api/v1/auth/password/forgot", json={"email": "neliswa@example.com"})
    token = re.search(r"reset=([A-Za-z0-9_-]+)", mails[-1].text).group(1)
    client.post("/api/v1/auth/password/reset", json={"token": token, "new_password": "Another-Strong-Pass-91"})

    with client.db_factory() as db:
        kinds = [n.type for n in db.query(Notification).all()]
    assert "security.password_changed" in kinds


# ------------------------------------------------------ reading and marking

def test_unread_count_and_marking_one_as_read(client, mails):
    user_id = make_user(client)
    headers = sign_in(client, mails)
    first = add(client, user_id, title="First")
    add(client, user_id, title="Second")

    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"unread": 3}

    assert client.post(f"/api/v1/notifications/{first}/read", headers=headers).json() == {"ok": True}
    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"unread": 2}

    # reading it twice is harmless
    assert client.post(f"/api/v1/notifications/{first}/read", headers=headers).status_code == 200


def test_mark_everything_read(client, mails):
    user_id = make_user(client)
    headers = sign_in(client, mails)
    for i in range(3):
        add(client, user_id, title=f"n{i}")

    assert client.post("/api/v1/notifications/read-all", headers=headers).json() == {"marked": 4}
    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"unread": 0}
    assert client.post("/api/v1/notifications/read-all", headers=headers).json() == {"marked": 0}


def test_newest_first_unread_filter_and_paging(client, mails):
    user_id = make_user(client)
    headers = sign_in(client, mails)
    ids = [add(client, user_id, title=f"n{i}") for i in range(5)]
    client.post(f"/api/v1/notifications/{ids[0]}/read", headers=headers)

    page = client.get("/api/v1/notifications?limit=3", headers=headers).json()
    assert [i["title"] for i in page["items"]] == ["n4", "n3", "n2"]
    assert page["next_before_id"] == ids[2]

    rest = client.get(f"/api/v1/notifications?limit=10&before_id={page['next_before_id']}", headers=headers).json()
    assert [i["title"] for i in rest["items"]][:2] == ["n1", "n0"]
    assert rest["next_before_id"] is None

    unread = client.get("/api/v1/notifications?unread_only=true&limit=50", headers=headers).json()
    assert all(not i["read"] for i in unread["items"]) and "n0" not in [i["title"] for i in unread["items"]]


def test_limits_are_enforced(client, mails):
    make_user(client)
    headers = sign_in(client, mails)
    assert client.get("/api/v1/notifications?limit=0", headers=headers).status_code == 422
    assert client.get("/api/v1/notifications?limit=101", headers=headers).status_code == 422


# ------------------------------------------------------------ who can see what

def test_people_only_ever_see_and_touch_their_own_notifications(client, mails):
    mine = make_user(client)
    theirs = make_user(client, email="other@example.com")
    my_headers = sign_in(client, mails)
    their_note = add(client, theirs, title="Private to them")
    add(client, mine, title="Mine")

    titles = [i["title"] for i in client.get("/api/v1/notifications?limit=50", headers=my_headers).json()["items"]]
    assert "Private to them" not in titles and "Mine" in titles

    assert client.post(f"/api/v1/notifications/{their_note}/read", headers=my_headers).status_code == 404

    client.post("/api/v1/notifications/read-all", headers=my_headers)
    with client.db_factory() as db:
        assert db.query(Notification).filter(Notification.id == their_note).one().read_at is None


def test_everything_needs_a_signed_in_user(client):
    for method, path in [
        ("get", "/api/v1/notifications"),
        ("get", "/api/v1/notifications/unread-count"),
        ("post", "/api/v1/notifications/read-all"),
        ("post", "/api/v1/notifications/1/read"),
    ]:
        assert getattr(client, method)(path).status_code == 401


# ----------------------------------------------------------------- the service

def test_links_can_only_point_inside_the_app():
    assert service.safe_link("/billing") == "/billing"
    assert service.safe_link("/trades?x=1") == "/trades?x=1"
    for bad in ["https://evil.example.com", "//evil.example.com", "javascript:alert(1)", "billing", "", None, "/a\\b", "/a\nb", "/" + "x" * 300]:
        assert service.safe_link(bad) is None


def test_a_bad_link_is_dropped_not_stored(client):
    user_id = make_user(client)
    add(client, user_id, link="https://evil.example.com")
    with client.db_factory() as db:
        assert db.query(Notification).one().link is None


def test_only_the_newest_200_are_kept(client):
    user_id = make_user(client)
    with client.db_factory() as db:
        for i in range(service.MAX_PER_USER + 5):
            service.notify(db, user_id, "test", f"n{i}")
        titles = [n.title for n in db.query(Notification).order_by(Notification.id).all()]
    assert len(titles) == service.MAX_PER_USER
    assert titles[0] == "n5" and titles[-1] == f"n{service.MAX_PER_USER + 4}"


def test_dedupe_only_applies_inside_its_window(client):
    user_id = make_user(client)
    with client.db_factory() as db:
        first = service.notify(db, user_id, "t", "x", body="same", dedupe_within=timedelta(hours=1))
        assert first is not None
        assert service.notify(db, user_id, "t", "x", body="same", dedupe_within=timedelta(hours=1)) is None
        assert service.notify(db, user_id, "t", "x", body="different", dedupe_within=timedelta(hours=1)) is not None
        first.created_at = first.created_at - timedelta(hours=2)
        db.commit()
        assert service.notify(db, user_id, "t", "x", body="same", dedupe_within=timedelta(hours=1)) is not None


def test_a_failure_never_breaks_the_caller():
    class Broken:
        def query(self, *a, **k):
            raise RuntimeError("database is down")

        def rollback(self):
            pass

    assert service.notify_safely(Broken(), 1, "t", "title") is None


def test_unknown_severity_falls_back_to_info(client):
    user_id = make_user(client)
    with client.db_factory() as db:
        assert service.notify(db, user_id, "t", "x", severity="<script>").severity == "info"


# ------------------------------------------------------------------ broadcast

def test_only_the_owner_can_broadcast(client, mails, monkeypatch):
    make_user(client, is_admin=True)
    make_user(client, email="member@example.com")
    admin_headers = sign_in(client, mails)
    member_headers = sign_in(client, mails, email="member@example.com")
    body = {"title": "Scheduled maintenance", "body": "Tonight at 22:00 UTC.", "link": "/dashboard", "severity": "warning"}

    assert client.post("/api/v1/admin/notifications/broadcast", json=body).status_code == 401
    assert client.post("/api/v1/admin/notifications/broadcast", json=body, headers=member_headers).status_code == 403

    sent = client.post("/api/v1/admin/notifications/broadcast", json=body, headers=admin_headers)
    assert sent.status_code == 201 and sent.json() == {"sent_to": 2}

    for headers in (admin_headers, member_headers):
        titles = [i["title"] for i in client.get("/api/v1/notifications?limit=50", headers=headers).json()["items"]]
        assert "Scheduled maintenance" in titles

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("OWNER_EMAIL", "someone-else@example.com")
    assert client.post("/api/v1/admin/notifications/broadcast", json=body, headers=admin_headers).status_code == 403


def test_broadcast_skips_suspended_accounts_and_rejects_outside_links(client, mails):
    make_user(client, is_admin=True)
    suspended = make_user(client, email="gone@example.com", is_active=False)
    headers = sign_in(client, mails)

    ok = client.post("/api/v1/admin/notifications/broadcast", json={"title": "Hello"}, headers=headers)
    assert ok.json() == {"sent_to": 1}
    with client.db_factory() as db:
        assert db.query(Notification).filter(Notification.user_id == suspended).count() == 0

    bad = client.post(
        "/api/v1/admin/notifications/broadcast",
        json={"title": "Click", "link": "https://evil.example.com"},
        headers=headers,
    )
    assert bad.status_code == 422

    assert client.post("/api/v1/admin/notifications/broadcast", json={"title": ""}, headers=headers).status_code == 422
    assert client.post("/api/v1/admin/notifications/broadcast", json={"title": "x", "severity": "security"}, headers=headers).status_code == 422
