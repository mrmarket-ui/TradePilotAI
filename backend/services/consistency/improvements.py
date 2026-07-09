from collections import defaultdict


def analyze_monthly_progress(trades):

    monthly = defaultdict(lambda: {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "profit": 0.0
    })

    for trade in trades:

        if not trade.closed_at:
            continue

        month = trade.closed_at.strftime("%Y-%m")

        stats = monthly[month]

        stats["trades"] += 1

        profit = trade.profit or 0

        stats["profit"] += profit

        if profit > 0:
            stats["wins"] += 1

        elif profit < 0:
            stats["losses"] += 1

    results = {}

    for month in sorted(monthly.keys()):

        data = monthly[month]

        total = data["trades"]

        win_rate = (
            data["wins"] / total * 100
            if total else 0
        )

        results[month] = {

            "trades": total,

            "wins": data["wins"],

            "losses": data["losses"],

            "profit": round(data["profit"], 2),

            "win_rate": round(win_rate, 2)

        }

    return results


def improvement_trend(trades):

    months = analyze_monthly_progress(trades)

    if len(months) < 2:
        return "Insufficient Data"

    profits = [
        m["profit"]
        for m in months.values()
    ]

    increasing = all(

        profits[i] >= profits[i - 1]

        for i in range(1, len(profits))

    )

    decreasing = all(

        profits[i] <= profits[i - 1]

        for i in range(1, len(profits))

    )

    if increasing:
        return "Improving"

    if decreasing:
        return "Declining"

    return "Mixed"
