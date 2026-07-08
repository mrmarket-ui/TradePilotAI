from models.trade import Trade


def analyze_behavior(trades):

    total = len(trades)

    revenge = 0
    overtrading = 0
    fomo = 0

    closed = sorted(
        [t for t in trades if t.closed_at],
        key=lambda x: x.closed_at
    )

    for i in range(1, len(closed)):

        previous = closed[i - 1]
        current = closed[i]

        if (
            previous.profit is not None
            and previous.profit < 0
        ):

            minutes = (
                current.opened_at -
                previous.closed_at
            ).total_seconds() / 60

            if minutes <= 15:
                revenge += 1

        if (
            previous.closed_at.date() ==
            current.closed_at.date()
        ):
            overtrading += 1

        if (
            current.take_profit
            and current.entry
            and current.exit_price
        ):

            target = abs(
                current.take_profit -
                current.entry
            )

            achieved = abs(
                current.exit_price -
                current.entry
            )

            if (
                target > 0
                and achieved < target * 0.35
                and (current.profit or 0) > 0
            ):
                fomo += 1

    return {

        "total_trades": total,

        "revenge_trades": revenge,

        "possible_overtrading": overtrading,

        "early_exit_trades": fomo

    }
