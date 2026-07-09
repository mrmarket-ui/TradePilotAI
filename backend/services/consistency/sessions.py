from collections import defaultdict


def get_session(hour):

    if hour is None:
        return "Unknown"

    if 0 <= hour < 8:
        return "Asian"

    if 8 <= hour < 13:
        return "London"

    if 13 <= hour < 17:
        return "New York"

    return "After Hours"


def analyze_sessions(trades):

    sessions = defaultdict(lambda: {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "profit": 0.0
    })

    for trade in trades:

        if not trade.opened_at:
            continue

        session = get_session(
            trade.opened_at.hour
        )

        sessions[session]["trades"] += 1

        profit = trade.profit or 0

        sessions[session]["profit"] += profit

        if profit > 0:
            sessions[session]["wins"] += 1

        elif profit < 0:
            sessions[session]["losses"] += 1

    results = {}

    for session, data in sessions.items():

        total = data["trades"]

        win_rate = (
            data["wins"] / total * 100
            if total else 0
        )

        results[session] = {

            "trades": total,

            "wins": data["wins"],

            "losses": data["losses"],

            "profit": round(data["profit"], 2),

            "win_rate": round(win_rate, 2)

        }

    return results
