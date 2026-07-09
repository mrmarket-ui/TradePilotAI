from collections import defaultdict


DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def analyze_weekdays(trades):

    weekdays = defaultdict(lambda: {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "profit": 0.0
    })

    for trade in trades:

        if not trade.opened_at:
            continue

        day = DAY_NAMES[trade.opened_at.weekday()]

        weekdays[day]["trades"] += 1

        profit = trade.profit or 0

        weekdays[day]["profit"] += profit

        if profit > 0:
            weekdays[day]["wins"] += 1

        elif profit < 0:
            weekdays[day]["losses"] += 1

    results = {}

    for day, data in weekdays.items():

        total = data["trades"]

        win_rate = (
            data["wins"] / total * 100
            if total else 0
        )

        results[day] = {

            "trades": total,

            "wins": data["wins"],

            "losses": data["losses"],

            "profit": round(data["profit"], 2),

            "win_rate": round(win_rate, 2)

        }

    return results


def best_weekday(trades):

    data = analyze_weekdays(trades)

    if not data:
        return None

    return max(
        data.items(),
        key=lambda item: item[1]["profit"]
    )


def worst_weekday(trades):

    data = analyze_weekdays(trades)

    if not data:
        return None

    return min(
        data.items(),
        key=lambda item: item[1]["profit"]
    )
