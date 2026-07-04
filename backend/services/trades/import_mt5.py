import MetaTrader5 as mt5
from datetime import datetime

from models.trade import Trade


def fetch_history(start, end):
    deals = mt5.history_deals_get(start, end)

    if deals is None:
        return []

    return deals