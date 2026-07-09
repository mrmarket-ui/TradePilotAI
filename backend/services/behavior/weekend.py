def detect_weekend_trading(trades):
    """
    Detects trades opened
    on Saturday or Sunday.
    """

    for trade in trades:

        if not trade.opened_at:
            continue

        if trade.opened_at.weekday() >= 5:
            return True

    return False