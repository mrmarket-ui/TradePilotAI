from datetime import datetime

import pytest
from pydantic import ValidationError

from schemas.trade import TradeCreate

BASE = dict(pair="EURUSD", direction="BUY", entry=1.10, stop_loss=1.09, take_profit=1.12)


def test_valid_open_and_close_times_are_parsed():
    trade = TradeCreate(**BASE, opened_at="2026-10-20T09:30", closed_at="2026-10-20T10:15")
    assert trade.opened_at == datetime(2026, 10, 20, 9, 30)
    assert trade.closed_at == datetime(2026, 10, 20, 10, 15)


def test_closing_before_opening_is_rejected():
    with pytest.raises(ValidationError) as error:
        TradeCreate(**BASE, opened_at="2026-10-20T10:15", closed_at="2026-10-20T09:30")
    assert "closed_at cannot be earlier than opened_at" in str(error.value)


def test_same_open_and_close_time_is_allowed():
    TradeCreate(**BASE, opened_at="2026-10-20T10:00", closed_at="2026-10-20T10:00")


def test_times_are_optional():
    assert TradeCreate(**BASE).opened_at is None
    assert TradeCreate(**BASE, opened_at="2026-10-20T10:00").closed_at is None
    assert TradeCreate(**BASE, closed_at="2026-10-20T10:00").opened_at is None


def test_mixing_timezone_aware_and_naive_times_does_not_crash():
    TradeCreate(**BASE, opened_at="2026-10-20T09:30", closed_at="2026-10-20T10:15+00:00")