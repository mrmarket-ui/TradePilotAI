import random
from datetime import datetime
from types import SimpleNamespace

from services.trades.positions import build_trade_rows

T0 = 1_760_000_000  # a fixed epoch second


def deal(ticket, position, kind, entry, price, volume=1.0, profit=0.0,
         commission=0.0, swap=0.0, time=T0, symbol="EURUSD", fee=0.0, magic=0, comment=""):
    return SimpleNamespace(
        ticket=ticket, position_id=position, type=kind, entry=entry, price=price,
        volume=volume, profit=profit, commission=commission, swap=swap, fee=fee,
        time=time, symbol=symbol, magic=magic, comment=comment,
    )


def round_trip(position, direction_buy=True, open_price=1.1000, close_price=1.1050,
               profit=50.0, time=T0, hold=3600, commission=-3.5, swap=0.0, symbol="EURUSD"):
    open_kind, close_kind = (0, 1) if direction_buy else (1, 0)
    return [
        deal(position * 10, position, open_kind, 0, open_price, commission=commission,
             time=time, symbol=symbol),
        deal(position * 10 + 1, position, close_kind, 1, close_price, profit=profit,
             commission=commission, swap=swap, time=time + hold, symbol=symbol),
    ]


def test_one_round_trip_becomes_one_trade_with_real_times_and_net_profit():
    deals = round_trip(1, profit=50.0, commission=-3.5, swap=-1.0)
    rows, summary = build_trade_rows(deals)
    assert len(rows) == 1
    row = rows[0]
    assert row["ticket"] == "1"
    assert row["direction"] == "BUY"
    assert row["entry"] == 1.1000 and row["exit_price"] == 1.1050
    assert row["profit"] == 50.0 - 3.5 - 3.5 - 1.0 == 42.0
    assert row["commission"] == -7.0 and row["swap"] == -1.0
    assert row["opened_at"] < row["closed_at"]
    assert (row["closed_at"] - row["opened_at"]).total_seconds() == 3600
    assert row["imported"] is True
    assert summary == {"positions": 1, "skipped_non_trade_deals": 0, "open_positions": 0, "reversals": 0}


def test_sell_positions_have_the_right_direction():
    rows, _ = build_trade_rows(round_trip(2, direction_buy=False, open_price=1.1, close_price=1.09, profit=100))
    assert rows[0]["direction"] == "SELL"


def test_account_operations_are_not_trades():
    balance = deal(1, 0, 2, 0, 0, profit=1000, symbol="", comment="Deposit")
    credit = deal(2, 0, 3, 0, 0, profit=100000, symbol="", comment="Bonus")
    rows, summary = build_trade_rows([balance, credit] + round_trip(3))
    assert len(rows) == 1
    assert summary["skipped_non_trade_deals"] == 2


def test_open_positions_are_not_imported_yet():
    still_open = [deal(5, 9, 0, 0, 1.2)]
    rows, summary = build_trade_rows(still_open + round_trip(4))
    assert [r["ticket"] for r in rows] == ["4"]
    assert summary["open_positions"] == 1


def test_partial_closes_use_volume_weighted_prices():
    deals = [
        deal(1, 7, 0, 0, 1.1000, volume=2.0, time=T0),
        deal(2, 7, 1, 1, 1.1100, volume=1.0, profit=100, time=T0 + 600),
        deal(3, 7, 1, 1, 1.1200, volume=1.0, profit=200, time=T0 + 1200),
    ]
    rows, _ = build_trade_rows(deals)
    assert len(rows) == 1
    assert rows[0]["lot_size"] == 2.0
    assert rows[0]["exit_price"] == 1.1150
    assert rows[0]["profit"] == 300.0
    assert (rows[0]["closed_at"] - rows[0]["opened_at"]).total_seconds() == 1200


def test_scaling_in_uses_the_average_entry_price():
    deals = [
        deal(1, 8, 0, 0, 1.1000, volume=1.0, time=T0),
        deal(2, 8, 0, 0, 1.1200, volume=3.0, time=T0 + 60),
        deal(3, 8, 1, 1, 1.1300, volume=4.0, profit=400, time=T0 + 600),
    ]
    rows, _ = build_trade_rows(deals)
    assert rows[0]["entry"] == 1.1150
    assert rows[0]["lot_size"] == 4.0


def test_a_position_whose_opening_deal_is_missing_has_no_open_time():
    # history that starts mid-position: only the closing deal is present
    rows, _ = build_trade_rows([deal(1, 11, 1, 1, 1.2, profit=30, time=T0)])
    assert rows[0]["opened_at"] is None
    assert rows[0]["closed_at"] is not None
    assert rows[0]["direction"] == "BUY"  # a closing SELL deal ends a BUY position


def test_reversals_are_counted_and_treated_as_exits():
    deals = [
        deal(1, 12, 0, 0, 1.1, time=T0),
        deal(2, 12, 1, 2, 1.2, profit=80, time=T0 + 100),
    ]
    rows, summary = build_trade_rows(deals)
    assert len(rows) == 1
    assert summary["reversals"] == 1


def test_input_order_does_not_matter():
    deals = []
    for position in range(1, 8):
        deals += round_trip(position, time=T0 + position * 10_000, profit=20 if position % 2 else -10)
    expected, _ = build_trade_rows(deals)
    shuffled = deals[:]
    random.Random(7).shuffle(shuffled)
    again, _ = build_trade_rows(shuffled)
    assert again == expected


def test_win_rate_is_not_diluted_by_entry_deals():
    deals = []
    for position in range(1, 11):
        winner = position <= 5
        deals += round_trip(position, time=T0 + position * 10_000, profit=60 if winner else -40, commission=0)
    rows, _ = build_trade_rows(deals)
    assert len(deals) == 20          # what the old importer turned into 20 "trades"
    assert len(rows) == 10
    wins = sum(1 for r in rows if r["profit"] > 0)
    assert wins / len(rows) == 0.5   # the old importer would have reported 25%


def test_times_do_not_depend_on_the_machine_time_zone():
    rows, _ = build_trade_rows(round_trip(1, time=1_760_000_000))
    assert rows[0]["opened_at"] == datetime(2025, 10, 9, 8, 53, 20)