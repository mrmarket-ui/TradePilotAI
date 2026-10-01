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


# ============================================================
# READ-ONLY MARKET DATA
# ============================================================

FOREX_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
    "NZD",
}


def normalize_forex_symbol(
    symbol: str,
) -> str | None:
    """
    Extract a supported 6-letter Forex pair from a broker
    symbol such as EURUSD, EURUSD.a or EURUSDm.

    Metals, crypto, indices and other non-Forex instruments
    are rejected.
    """

    if not symbol:
        return None

    cleaned = "".join(
        character
        for character in symbol.upper()
        if character.isalpha()
    )

    if len(cleaned) < 6:
        return None

    candidate = cleaned[:6]

    base = candidate[:3]
    quote = candidate[3:6]

    if (
        base not in FOREX_CURRENCIES
        or quote not in FOREX_CURRENCIES
        or base == quote
    ):
        return None

    return candidate


def resolve_forex_symbol(
    requested_symbol: str,
):
    """
    Resolve a canonical Forex pair such as EURUSD to the
    broker's actual symbol, including suffixes/prefixes.

    Read-only. Does not place or modify trades.
    """

    if not MT5_AVAILABLE:
        return None

    canonical = normalize_forex_symbol(
        requested_symbol,
    )

    if canonical is None:
        return None

    symbols = mt5.symbols_get()

    if symbols is None:
        return None

    exact_match = None
    candidates = []

    requested_upper = (
        requested_symbol
        .strip()
        .upper()
    )

    for info in symbols:
        broker_symbol = str(
            info.name
        )

        broker_upper = (
            broker_symbol
            .strip()
            .upper()
        )

        broker_canonical = (
            normalize_forex_symbol(
                broker_symbol,
            )
        )

        if broker_canonical != canonical:
            continue

        if broker_upper == requested_upper:
            exact_match = broker_symbol
            break

        candidates.append(
            broker_symbol,
        )

    if exact_match:
        return exact_match

    if not candidates:
        return None

    candidates.sort(
        key=lambda value: (
            len(value),
            value,
        ),
    )

    return candidates[0]


def get_symbol_info(
    symbol: str,
):
    """
    Return basic read-only MT5 symbol information.
    """

    if not MT5_AVAILABLE:
        return None

    resolved = resolve_forex_symbol(
        symbol,
    )

    if resolved is None:
        return None

    info = mt5.symbol_info(
        resolved,
    )

    if info is None:
        return None

    return {
        "requested_symbol": symbol,
        "symbol": resolved,
        "canonical_symbol":
            normalize_forex_symbol(
                resolved,
            ),
        "digits": info.digits,
        "point": info.point,
        "spread": info.spread,
        "trade_mode": info.trade_mode,
        "visible": info.visible,
    }


def get_tick(
    symbol: str,
):
    """
    Return the latest read-only bid/ask tick.
    """

    if not MT5_AVAILABLE:
        return None

    resolved = resolve_forex_symbol(
        symbol,
    )

    if resolved is None:
        return None

    if not mt5.symbol_select(
        resolved,
        True,
    ):
        return None

    tick = mt5.symbol_info_tick(
        resolved,
    )

    if tick is None:
        return None

    return {
        "symbol": resolved,
        "canonical_symbol":
            normalize_forex_symbol(
                resolved,
            ),
        "bid": float(tick.bid),
        "ask": float(tick.ask),
        "last": float(tick.last),
        "time": int(tick.time),
    }


def _timeframe_value(
    timeframe: str,
):
    if not MT5_AVAILABLE:
        return None

    values = {
        "H1": mt5.TIMEFRAME_H1,
        "M15": mt5.TIMEFRAME_M15,
        "M5": mt5.TIMEFRAME_M5,
    }

    return values.get(
        timeframe.upper(),
    )


def get_candles(
    symbol: str,
    timeframe: str,
    count: int = 200,
):
    """
    Read H1/M15/M5 OHLC candles from MT5.

    The currently-forming candle is intentionally excluded.
    Only completed candles are returned to the strategy
    analysis layer.
    """

    if not MT5_AVAILABLE:
        return []

    if count <= 0:
        return []

    timeframe_value = (
        _timeframe_value(
            timeframe,
        )
    )

    if timeframe_value is None:
        return []

    resolved = resolve_forex_symbol(
        symbol,
    )

    if resolved is None:
        return []

    if not mt5.symbol_select(
        resolved,
        True,
    ):
        return []

    rates = mt5.copy_rates_from_pos(
        resolved,
        timeframe_value,

        # Position zero is the currently-forming candle.
        # Start at one so strategy analysis only sees
        # completed market data.
        1,

        count,
    )

    if rates is None:
        return []

    candles = []

    for rate in rates:
        candles.append(
            {
                "time": int(
                    rate["time"],
                ),
                "open": float(
                    rate["open"],
                ),
                "high": float(
                    rate["high"],
                ),
                "low": float(
                    rate["low"],
                ),
                "close": float(
                    rate["close"],
                ),
                "tick_volume": int(
                    rate["tick_volume"],
                ),
                "spread": int(
                    rate["spread"],
                ),
            }
        )

    return candles


def get_multi_timeframe_market_data(
    symbol: str,
    candle_count: int = 200,
):
    """
    Read the market snapshot required by TradePilotAI's
    proposal engine.

    This function is deliberately read-only.
    """

    resolved = resolve_forex_symbol(
        symbol,
    )

    if resolved is None:
        return None

    canonical = normalize_forex_symbol(
        resolved,
    )

    return {
        "symbol": resolved,
        "canonical_symbol": canonical,

        "symbol_info":
            get_symbol_info(
                resolved,
            ),

        "tick":
            get_tick(
                resolved,
            ),

        "timeframes": {
            "H1": get_candles(
                resolved,
                "H1",
                candle_count,
            ),
            "M15": get_candles(
                resolved,
                "M15",
                candle_count,
            ),
            "M5": get_candles(
                resolved,
                "M5",
                candle_count,
            ),
        },
    }
