def analyze_holding_behavior(
    trades,
):
    """
    Detects:

    Holding losers too long

    Cutting winners too early
    """

    winner_hours = []

    loser_hours = []

    for trade in trades:

        if (
            not trade.opened_at
            or not trade.closed_at
        ):
            continue

        duration = (

            trade.closed_at
            - trade.opened_at

        ).total_seconds() / 3600

        if (trade.profit or 0) > 0:

            winner_hours.append(duration)

        elif (trade.profit or 0) < 0:

            loser_hours.append(duration)

    if (
        not winner_hours
        or not loser_hours
    ):

        return {

            "holding_losers_too_long": False,

            "cutting_winners_too_early": False,

        }

    avg_win = sum(winner_hours) / len(winner_hours)

    avg_loss = sum(loser_hours) / len(loser_hours)

    return {

        "holding_losers_too_long":

            avg_loss > avg_win * 1.5,

        "cutting_winners_too_early":

            avg_win < avg_loss * 0.75,

    }