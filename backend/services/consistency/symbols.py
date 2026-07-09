from collections import defaultdict


def get_symbol(trade):

    if hasattr(trade, "pair"):
        return trade.pair

    if hasattr(trade, "symbol"):
        return trade.symbol

    return "Unknown"


def analyze_symbols(trades):

    symbols = defaultdict(lambda: {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "profit": 0.0,
        "average_profit": 0.0,
        "average_loss": 0.0,
        "gross_profit": 0.0,
        "gross_loss": 0.0
    })

    for trade in trades:

        symbol = get_symbol(trade)

        profit = trade.profit or 0

        stats = symbols[symbol]

        stats["trades"] += 1

        stats["profit"] += profit

        if profit > 0:

            stats["wins"] += 1

            stats["gross_profit"] += profit

        elif profit < 0:

            stats["losses"] += 1

            stats["gross_loss"] += abs(profit)

    results = {}

    for symbol, data in symbols.items():

        trades_count = data["trades"]

        wins = data["wins"]

        losses = data["losses"]

        avg_profit = (
            data["gross_profit"] / wins
            if wins else 0
        )

        avg_loss = (
            data["gross_loss"] / losses
            if losses else 0
        )

        win_rate = (
            wins / trades_count * 100
            if trades_count else 0
        )

        results[symbol] = {

            "trades": trades_count,

            "wins": wins,

            "losses": losses,

            "profit": round(data["profit"], 2),

            "gross_profit": round(data["gross_profit"], 2),

            "gross_loss": round(data["gross_loss"], 2),

            "average_profit": round(avg_profit, 2),

            "average_loss": round(avg_loss, 2),

            "win_rate": round(win_rate, 2)

        }

    return results


def best_symbol(trades):

    data = analyze_symbols(trades)

    if not data:
        return None

    return max(
        data.items(),
        key=lambda item: item[1]["profit"]
    )


def worst_symbol(trades):

    data = analyze_symbols(trades)

    if not data:
        return None

    return min(
        data.items(),
        key=lambda item: item[1]["profit"]
    )
