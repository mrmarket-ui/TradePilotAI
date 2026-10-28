from types import SimpleNamespace

import pytest

T0 = 1_760_000_000


def deal(ticket, position, kind, entry, price, profit=0.0, time=T0, symbol="EURUSD"):
    return SimpleNamespace(
        ticket=ticket, position_id=position, type=kind, entry=entry, price=price,
        volume=1.0, profit=profit, commission=0.0, swap=0.0, fee=0.0,
        time=time, symbol=symbol, magic=0, comment="",
    )


def two_positions_and_a_deposit():
    return [
        deal(1, 0, 2, 0, 0, profit=500, symbol=""),          # deposit
        deal(10, 1, 0, 0, 1.10, time=T0),
        deal(11, 1, 1, 1, 1.11, profit=100, time=T0 + 600),
        deal(20, 2, 1, 0, 1.12, time=T0 + 1000),
        deal(21, 2, 0, 1, 1.13, profit=-100, time=T0 + 2000),
    ]


class FakeTrade:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _sync():
    try:
        import services.trades.sync as module
    except Exception as exc:
        pytest.skip(f"sync module not importable here: {exc}")
    return module


def _run(monkeypatch, deals, already_saved=(), connected=True):
    module = _sync()
    saved = []

    def fake_save(db, trade):
        if trade.ticket in already_saved:
            return False
        saved.append(trade)
        return True

    monkeypatch.setattr(module, "Trade", FakeTrade)
    monkeypatch.setattr(module, "decrypt", lambda value: "secret")
    monkeypatch.setattr(
        module, "connect",
        lambda account, password, server: (connected, "Connected" if connected else "Bad login"),
    )
    monkeypatch.setattr(module, "disconnect", lambda: None)
    monkeypatch.setattr(module, "get_history", lambda start, end: deals)
    monkeypatch.setattr(module, "save_trade", fake_save)

    account = SimpleNamespace(
        encrypted_password="x", account_number="1234", server="Srv-Live",
        user_id=7, broker="Headway", last_sync=None,
    )
    db = SimpleNamespace(commit=lambda: None, rollback=lambda: None)

    return module.sync_account(db, account), saved, account


def test_one_trade_per_position_and_deposits_are_ignored(monkeypatch):
    result, saved, account = _run(monkeypatch, two_positions_and_a_deposit())
    assert result["success"] is True
    assert result["imported"] == 2 and result["skipped"] == 0
    assert result["positions"] == 2
    assert result["ignored_non_trade_deals"] == 1
    assert len(saved) == 2
    assert {t.direction for t in saved} == {"BUY", "SELL"}
    assert account.last_sync is not None


def test_tickets_are_namespaced_by_server_and_account(monkeypatch):
    _, saved, _ = _run(monkeypatch, two_positions_and_a_deposit())
    assert sorted(t.ticket for t in saved) == [
        "mt5:Srv-Live:1234:1",
        "mt5:Srv-Live:1234:2",
    ]


def test_trades_belong_to_the_account_owner(monkeypatch):
    _, saved, _ = _run(monkeypatch, two_positions_and_a_deposit())
    assert all(t.user_id == 7 and t.broker == "Headway" and t.imported is True for t in saved)


def test_trades_already_imported_are_counted_as_skipped(monkeypatch):
    result, saved, _ = _run(
        monkeypatch,
        two_positions_and_a_deposit(),
        already_saved=("mt5:Srv-Live:1234:1",),
    )
    assert result["imported"] == 1 and result["skipped"] == 1
    assert len(saved) == 1


def test_a_failed_login_imports_nothing(monkeypatch):
    result, saved, account = _run(monkeypatch, two_positions_and_a_deposit(), connected=False)
    assert result == {"success": False, "message": "Bad login"}
    assert saved == []
    assert account.last_sync is None