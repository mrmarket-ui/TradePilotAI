"""
TradePilot AI AutoTrader approval rules.

Pure functions (no database) so they are easy to test. Each returns a
human-readable violation message, or None when the proposal is acceptable.
"""

from __future__ import annotations


def proposal_rule_violation(
    direction,
    entry,
    stop,
    target,
    risk_percent,
    max_risk_percent,
) -> str | None:
    side = str(direction or "").strip().upper()

    if side not in ("BUY", "SELL"):
        return "The proposal has an invalid trade direction."

    try:
        entry = float(entry)
        stop = float(stop)
        target = float(target)
    except (TypeError, ValueError):
        return "The proposal has invalid price levels."

    if side == "BUY":
        levels_ok = stop < entry < target
    else:
        levels_ok = target < entry < stop

    if not levels_ok:
        return (
            "Stop loss and take profit are on the wrong side "
            "of the entry price."
        )

    try:
        risk = float(risk_percent)
    except (TypeError, ValueError):
        return "The proposal has an invalid risk percentage."

    if not risk > 0:
        return "The proposal has an invalid risk percentage."

    if max_risk_percent is not None and risk > float(max_risk_percent):
        return (
            "The proposed risk exceeds the strategy's maximum "
            "risk per trade."
        )

    return None


def daily_trade_limit_reached(
    approved_today: int,
    max_trades_per_day,
) -> bool:
    if max_trades_per_day is None:
        return False

    return approved_today >= max_trades_per_day