def detect_fomo(
    trades,
):
    """
    Simple FOMO detector.

    Looks for entries far from stop loss
    relative to take profit.

    Will be upgraded later using ATR.
    """

    count = 0

    total = 0

    for trade in trades:

        if (

            trade.entry is None
            or trade.stop_loss is None
            or trade.take_profit is None

        ):

            continue

        risk = abs(
            trade.entry -
            trade.stop_loss
        )

        reward = abs(
            trade.take_profit -
            trade.entry
        )

        if risk == 0:
            continue

        rr = reward / risk

        total += 1

        if rr < 1:

            count += 1

    if total == 0:
        return False

    return count / total > 0.4