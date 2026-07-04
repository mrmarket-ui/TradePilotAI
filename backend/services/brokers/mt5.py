import MetaTrader5 as mt5
from datetime import datetime


def login(account: int, password: str, server: str):
    if not mt5.initialize():
        return False, "MetaTrader5 failed to initialize."

    authorized = mt5.login(
        login=account,
        password=password,
        server=server
    )

    if not authorized:
        error = mt5.last_error()
        mt5.shutdown()
        return False, error

    return True, "Connected"


def shutdown():
    mt5.shutdown()


def get_history(start: datetime, end: datetime):
    deals = mt5.history_deals_get(start, end)

    if deals is None:
        return []

    return deals


def get_open_positions():
    positions = mt5.positions_get()

    if positions is None:
        return []

    return positions