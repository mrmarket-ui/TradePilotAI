from datetime import datetime

from services.brokers.mt5 import get_history


def import_history():

    start = datetime(2000, 1, 1)

    end = datetime.now()

    return get_history(start, end)