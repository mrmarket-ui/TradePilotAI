"""
The token-signing key must come from the environment, never from the code.

These tests start a fresh Python process for each case, because the settings
are read once when the module is first imported.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
GOOD_KEY = "k" * 64
SHOW = "import config.security as s; print(s.ALGORITHM, s.ACCESS_TOKEN_EXPIRE_MINUTES, len(s.SECRET_KEY))"


def start(**env):
    # Values are passed explicitly (even empty ones) so a real backend/.env
    # file cannot fill in a value the test deliberately left out.
    return subprocess.run(
        [sys.executable, "-c", SHOW],
        cwd=BACKEND,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_a_good_key_loads():
    result = start(SECRET_KEY=GOOD_KEY, ACCESS_TOKEN_EXPIRE_MINUTES="60")
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["HS256", "60", "64"]


def test_a_missing_key_stops_the_app():
    result = start(SECRET_KEY="")
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_a_short_key_stops_the_app_without_printing_it():
    result = start(SECRET_KEY="tooshort-secret")
    assert result.returncode != 0
    assert "tooshort-secret" not in result.stderr + result.stdout


def test_the_algorithm_cannot_be_changed_from_the_environment():
    result = start(SECRET_KEY=GOOD_KEY, ALGORITHM="none")
    assert result.returncode == 0, result.stderr
    assert result.stdout.split()[0] == "HS256"


def test_token_lifetime_is_clamped_to_a_sensible_range():
    assert start(SECRET_KEY=GOOD_KEY, ACCESS_TOKEN_EXPIRE_MINUTES="1").stdout.split()[1] == "5"
    assert start(SECRET_KEY=GOOD_KEY, ACCESS_TOKEN_EXPIRE_MINUTES="99999").stdout.split()[1] == "1440"
    assert start(SECRET_KEY=GOOD_KEY, ACCESS_TOKEN_EXPIRE_MINUTES="abc").stdout.split()[1] == "60"
    assert start(SECRET_KEY=GOOD_KEY, ACCESS_TOKEN_EXPIRE_MINUTES="30").stdout.split()[1] == "30"


def test_the_settings_file_contains_no_quoted_key():
    source = (BACKEND / "config" / "security.py").read_text(encoding="utf-8")
    assert not re.search(r"""SECRET_KEY\s*=\s*["']""", source)