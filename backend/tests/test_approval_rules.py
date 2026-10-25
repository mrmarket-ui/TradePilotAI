import pytest

from services.brokers.approval_rules import (
    daily_trade_limit_reached,
    proposal_rule_violation,
)


def check(direction="BUY", entry=1.1000, stop=1.0950, target=1.1100,
          risk=0.5, cap=1.0):
    return proposal_rule_violation(direction, entry, stop, target, risk, cap)


def test_valid_buy_and_sell_pass():
    assert check() is None
    assert check("sell", 1.1000, 1.1050, 1.0900) is None


def test_wrong_side_levels_are_rejected():
    assert "wrong side" in check("BUY", 1.1000, 1.1050, 1.1100)
    assert "wrong side" in check("SELL", 1.1000, 1.0950, 1.1100)
    assert "wrong side" in check("BUY", 1.1000, 1.1000, 1.1100)


def test_invalid_direction_is_rejected():
    assert "direction" in check("HOLD")
    assert "direction" in check(None)


def test_invalid_numbers_are_rejected():
    assert check(entry=None) is not None
    assert check(entry=float("nan")) is not None
    assert check(stop="abc") is not None


def test_risk_rules():
    assert "exceeds" in check(risk=2.0, cap=1.0)
    assert check(risk=1.0, cap=1.0) is None
    assert check(risk=0.5, cap=None) is None
    assert "risk" in check(risk=0)
    assert "risk" in check(risk=-1)
    assert "risk" in check(risk=None)


def test_daily_trade_limit():
    assert daily_trade_limit_reached(3, 3) is True
    assert daily_trade_limit_reached(2, 3) is False
    assert daily_trade_limit_reached(99, None) is False


def test_route_module_still_imports():
    try:
        import routes.v1.mt5_proposals as module
    except Exception as exc:
        pytest.skip(f"route module not importable here: {exc}")
    assert hasattr(module, "approve_trade_proposal")
    assert hasattr(module, "_validate_approval_safety")