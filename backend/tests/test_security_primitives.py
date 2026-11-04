"""
Tests for the building blocks of email login codes, password-reset links and
the password policy. Everything here is pure, so it needs no database.
"""

from datetime import datetime, timedelta

import pytest

from services.security import otp, password_policy, tokens

NOW = datetime(2026, 10, 29, 12, 0, 0)


@pytest.fixture(autouse=True)
def secret(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "k" * 40)


# ---------------- one-time codes ----------------

def test_codes_are_six_digits():
    assert otp.OTP_LENGTH == 6
    for _ in range(50):
        code = otp.generate_code()
        assert len(code) == 6 and code.isdigit()


def test_codes_are_not_all_the_same():
    assert len({otp.generate_code() for _ in range(40)}) > 20


def test_the_stored_hash_does_not_contain_the_code():
    stored = otp.hash_code("123456", "challenge-1")
    assert "123456" not in stored and len(stored) == 64


def test_a_hash_depends_on_the_challenge_and_the_server_secret(monkeypatch):
    base = otp.hash_code("123456", "challenge-1")
    assert base == otp.hash_code("123456", "challenge-1")
    assert base != otp.hash_code("123456", "challenge-2")
    monkeypatch.setenv("SECRET_KEY", "z" * 40)
    assert base != otp.hash_code("123456", "challenge-1")


def test_the_hash_cannot_be_made_without_a_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY")
    with pytest.raises(RuntimeError):
        otp.hash_code("123456", "challenge-1")


def test_the_right_code_matches_even_with_spaces_or_dashes():
    stored = otp.hash_code("123456", "c")
    assert otp.code_matches("123456", "c", stored)
    assert otp.code_matches("123 456", "c", stored)
    assert otp.code_matches("123-456", "c", stored)


def test_wrong_short_long_and_odd_codes_do_not_match():
    stored = otp.hash_code("123456", "c")
    for bad in ["654321", "12345", "1234567", "", None, 123456.0, "abcdef", "123456 7"]:
        assert not otp.code_matches(bad, "c", stored)


def test_a_code_does_not_work_for_another_challenge():
    stored = otp.hash_code("123456", "c1")
    assert not otp.code_matches("123456", "c2", stored)


def test_challenge_ids_are_unguessable_and_unique():
    ids = {otp.new_challenge_id() for _ in range(50)}
    assert len(ids) == 50 and all(len(i) >= 40 for i in ids)


def _check(submitted="123456", attempts=0, consumed=None, expires=None, now=NOW):
    stored = otp.hash_code("123456", "c")
    return otp.check_attempt(
        submitted=submitted, challenge_id="c", code_hash=stored,
        expires_at=expires or NOW + timedelta(minutes=5),
        attempts=attempts, consumed_at=consumed, now=now,
    )


def test_attempt_states():
    assert _check() == "ok"
    assert _check("000000") == "wrong"
    assert _check(consumed=NOW) == "used"
    assert _check(expires=NOW - timedelta(seconds=1)) == "expired"
    assert _check(expires=NOW) == "expired"
    assert _check(attempts=otp.OTP_MAX_ATTEMPTS) == "locked"
    assert _check(attempts=otp.OTP_MAX_ATTEMPTS - 1) == "ok"


def test_a_locked_challenge_stays_locked_even_for_the_right_code():
    assert _check("123456", attempts=otp.OTP_MAX_ATTEMPTS) == "locked"


def test_a_used_code_cannot_be_replayed():
    assert _check("123456", consumed=NOW) == "used"


def test_expiry_is_ten_minutes():
    assert otp.expiry_time(NOW) == NOW + timedelta(minutes=10)


def test_resend_rules():
    assert otp.resend_allowed(last_sent_at=NOW - timedelta(seconds=61), resend_count=0, now=NOW) == (True, 0)
    allowed, wait = otp.resend_allowed(last_sent_at=NOW - timedelta(seconds=20), resend_count=0, now=NOW)
    assert allowed is False and 39 <= wait <= 41
    assert otp.resend_allowed(last_sent_at=NOW - timedelta(hours=1), resend_count=otp.OTP_MAX_RESENDS, now=NOW) == (False, 0)


def test_email_masking():
    assert otp.mask_email("neliswa@gmail.com") == "n***@gmail.com"
    assert otp.mask_email("") == "your email"
    assert otp.mask_email("nope") == "your email"


def test_weak_secret_keys_are_reported(monkeypatch):
    assert otp.secret_key_problem() is None
    monkeypatch.setenv("SECRET_KEY", "short")
    assert "shorter" in otp.secret_key_problem()
    monkeypatch.delenv("SECRET_KEY")
    assert "not set" in otp.secret_key_problem()


# ---------------- reset tokens ----------------

def test_reset_tokens_are_unique_and_only_the_hash_is_stored():
    raw, stored = tokens.new_token()
    other_raw, _ = tokens.new_token()
    assert raw != other_raw
    assert stored != raw and len(stored) == 64
    assert tokens.token_matches(raw, stored)


def test_reset_tokens_do_not_match_other_values():
    raw, stored = tokens.new_token()
    assert not tokens.token_matches(raw + "x", stored)
    assert not tokens.token_matches("", stored)
    assert not tokens.token_matches(None, stored)
    assert not tokens.token_matches("short", stored)
    assert not tokens.token_matches("a" * 43 + "!", stored)
    assert not tokens.token_matches(raw, "")


def test_token_shape_check():
    raw, _ = tokens.new_token()
    assert tokens.is_plausible_token(raw)
    assert not tokens.is_plausible_token("x" * 10)
    assert not tokens.is_plausible_token(12345)
    assert tokens.RESET_TOKEN_TTL_MINUTES == 30


# ---------------- password policy ----------------

def test_a_reasonable_password_is_accepted():
    assert password_policy.validate_password("Correct-Horse-47-Battery", "neliswa@example.com") == []
    assert password_policy.validate_password("a long passphrase with spaces", "x@y.com") == []


def test_short_passwords_are_rejected():
    assert any("at least" in p for p in password_policy.validate_password("Ab1!x"))


def test_common_passwords_are_rejected_even_with_digits_added():
    assert any("common" in p for p in password_policy.validate_password("password123"))
    assert any("common" in p for p in password_policy.validate_password("TradePilot"))
    assert any("common" in p for p in password_policy.validate_password("qwertyuiop"))


def test_repeats_and_sequences_are_rejected():
    assert any("sequential" in p for p in password_policy.validate_password("aaaaaaaaaaaa"))
    assert any("sequential" in p for p in password_policy.validate_password("1234567890"))
    assert any("sequential" in p for p in password_policy.validate_password("abcdefghij"))
    assert any("sequential" in p for p in password_policy.validate_password("0987654321"))
    assert any("sequential" in p for p in password_policy.validate_password("asdfghjkl"))
    assert password_policy.validate_password("Tr4de-Pilot-Rocks-99") == []


def test_the_email_name_cannot_be_the_password():
    problems = password_policy.validate_password("neliswa-2026-xyz", "neliswa@example.com")
    assert any("email" in p for p in problems)
    assert password_policy.validate_password("neliswa-2026-xyz", "ab@example.com") == []


def test_passwords_longer_than_72_bytes_are_rejected():
    assert any("72" in p for p in password_policy.validate_password("x1Y" * 30))
    assert any("72" in p for p in password_policy.validate_password("é" * 40))
    assert password_policy.validate_password("Qz7!" * 17) == []