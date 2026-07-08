from services.analytics.risk import (
    calculate_max_drawdown,
    calculate_expectancy,
)


def psychology_score(trades):

    if not trades:

        return {
            "discipline": 0,
            "consistency": 0,
            "patience": 0,
            "overall": 0
        }

    expectancy = calculate_expectancy(trades)

    drawdown = calculate_max_drawdown(trades)

    discipline = max(
        0,
        100 - drawdown
    )

    consistency = min(
        100,
        50 + expectancy
    )

    patience = 100

    for trade in trades:

        if (
            trade.profit
            and trade.profit < 0
        ):
            patience -= 1

    patience = max(
        0,
        patience
    )

    overall = round(
        (
            discipline +
            consistency +
            patience
        ) / 3,
        2
    )

    return {

        "discipline": round(discipline,2),

        "consistency": round(consistency,2),

        "patience": round(patience,2),

        "overall": overall

    }
