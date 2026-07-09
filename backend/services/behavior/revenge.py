from datetime import timedelta


def detect_revenge_trading(
    trades,
    cooldown_minutes=30,
):
    """
    Revenge trading:

    Opening a new trade shortly
    after closing a losing trade.
    """

    losing_trades = sorted(

        [
            t
            for t in trades
            if (
                t.closed_at
                and (t.profit or 0) < 0
            )
        ],

        key=lambda t: t.closed_at

    )

    for trade in losing_trades:

        for next_trade in trades:

            if not next_trade.opened_at:
                continue

            if next_trade.opened_at <= trade.closed_at:
                continue

            if (
                next_trade.opened_at
                - trade.closed_at
            ) <= timedelta(
                minutes=cooldown_minutes
            ):

                return True

    return False