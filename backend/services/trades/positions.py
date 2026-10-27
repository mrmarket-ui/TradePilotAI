"""
TradePilot AI MT5 position builder.

MetaTrader reports history as individual deals, not trades. One real trade
(a position) normally produces an ENTRY deal that opens it and an EXIT deal
that closes it, and the account also records non-trade operations such as
deposits, withdrawals, credits and bonuses. Importing every deal as a trade
double-counts trades, dilutes the win rate and turns deposits into "trades".

This module is pure (no database or MT5 import) so it is easy to test.
It returns plain dictionaries; the caller turns them into Trade rows.

Conventions
-----------
* One row per CLOSED position (positions that are still open are skipped).
* profit is the net result that reached the account:
  profit + commission + swap + fee over every deal of the position.
* Times are the broker server clock, stored as naive datetimes without
  depending on the time zone of the machine running TradePilot.
* stop_loss and take_profit are 0 when unknown (deals do not carry them).
* A reversal (an IN/OUT deal) is treated as the exit of the old position;
  its opening half is not imported separately. It is counted in the summary.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

DEAL_TYPE_BUY = 0
DEAL_TYPE_SELL = 1

DEAL_ENTRY_IN = 0
DEAL_ENTRY_OUT = 1
DEAL_ENTRY_INOUT = 2
DEAL_ENTRY_OUT_BY = 3

_EXIT_ENTRIES = (DEAL_ENTRY_OUT, DEAL_ENTRY_INOUT, DEAL_ENTRY_OUT_BY)


def _clock(seconds: Any) -> datetime:
    return datetime.fromtimestamp(
        int(seconds),
        tz=timezone.utc,
    ).replace(tzinfo=None)


def _volume(deals: list) -> float:
    return sum(float(getattr(d, "volume", 0) or 0) for d in deals)


def _weighted_price(deals: list) -> float:
    total = _volume(deals)

    if total <= 0:
        return float(deals[0].price)

    return sum(
        float(d.price) * float(getattr(d, "volume", 0) or 0)
        for d in deals
    ) / total


def _money(deals: list, field: str) -> float:
    return sum(float(getattr(d, field, 0) or 0) for d in deals)


def build_trade_rows(deals: Iterable[Any]) -> tuple[list[dict], dict]:
    groups: dict[int, list] = defaultdict(list)
    skipped = 0

    for deal in deals:
        if (
            deal.type not in (DEAL_TYPE_BUY, DEAL_TYPE_SELL)
            or not getattr(deal, "symbol", "")
            or not getattr(deal, "position_id", 0)
        ):
            skipped += 1
            continue

        groups[int(deal.position_id)].append(deal)

    rows: list[dict] = []
    open_positions = 0
    reversals = 0

    for position_id in sorted(groups):
        group = sorted(groups[position_id], key=lambda d: (d.time, d.ticket))

        entries = [d for d in group if d.entry == DEAL_ENTRY_IN]
        exits = [d for d in group if d.entry in _EXIT_ENTRIES]

        reversals += sum(1 for d in exits if d.entry == DEAL_ENTRY_INOUT)

        if not exits:
            open_positions += 1
            continue

        if entries:
            reference = entries[0]
            direction = "BUY" if reference.type == DEAL_TYPE_BUY else "SELL"
            lots = _volume(entries)
            entry_price = _weighted_price(entries)
            opened_at = _clock(reference.time)
        else:
            # History starts mid-position: the opening deal is missing.
            reference = exits[0]
            direction = "SELL" if reference.type == DEAL_TYPE_BUY else "BUY"
            lots = _volume(exits)
            entry_price = _weighted_price(exits)
            opened_at = None

        net = (
            _money(group, "profit")
            + _money(group, "commission")
            + _money(group, "swap")
            + _money(group, "fee")
        )

        rows.append(
            {
                "ticket": str(position_id),
                "pair": reference.symbol,
                "direction": direction,
                "entry": round(entry_price, 8),
                "exit_price": round(_weighted_price(exits), 8),
                "stop_loss": 0.0,
                "take_profit": 0.0,
                "lot_size": round(lots, 8),
                "profit": round(net, 2),
                "commission": round(_money(group, "commission"), 2),
                "swap": round(_money(group, "swap"), 2),
                "magic_number": int(getattr(reference, "magic", 0) or 0) or None,
                "comment": getattr(reference, "comment", None) or None,
                "opened_at": opened_at,
                "closed_at": _clock(exits[-1].time),
                "imported": True,
            }
        )

    summary = {
        "positions": len(rows),
        "skipped_non_trade_deals": skipped,
        "open_positions": open_positions,
        "reversals": reversals,
    }

    return rows, summary