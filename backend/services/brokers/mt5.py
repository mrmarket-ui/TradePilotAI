try:
    import MetaTrader5 as mt5

    MT5_AVAILABLE = True
    MT5_IMPORT_ERROR = None

except ImportError as exc:
    mt5 = None
    MT5_AVAILABLE = False
    MT5_IMPORT_ERROR = str(exc)


def is_available() -> bool:
    return MT5_AVAILABLE


def connect(
    account: int,
    password: str,
    server: str,
):
    if not MT5_AVAILABLE:
        return (
            False,
            (
                "MetaTrader 5 integration is not available "
                "on this server. MT5 broker connectivity "
                "requires the Windows MT5 runtime."
            ),
        )

    if not mt5.initialize():
        return (
            False,
            "MetaTrader5 failed to initialize.",
        )

    authorized = mt5.login(
        login=account,
        password=password,
        server=server,
    )

    if not authorized:
        error = mt5.last_error()
        mt5.shutdown()

        return False, error

    return True, "Connected"


def disconnect():
    if MT5_AVAILABLE:
        mt5.shutdown()


def get_history(
    start,
    end,
):
    if not MT5_AVAILABLE:
        return []

    deals = mt5.history_deals_get(
        start,
        end,
    )

    if deals is None:
        return []

    return deals
