import MetaTrader5 as mt5


def connect(
    account: int,
    password: str,
    server: str
):

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


def disconnect():
    mt5.shutdown()


def get_history(start, end):

    deals = mt5.history_deals_get(
        start,
        end
    )

    if deals is None:
        return []

    return deals