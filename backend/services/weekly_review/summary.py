def generate_weekly_summary(
    metrics: dict,
    behavior: dict,
) -> str:
    total = metrics.get("total_trades", 0)

    if total == 0:
        return (
            "No completed trades were recorded during this review period."
        )

    win_rate = metrics.get("win_rate", 0)
    net_profit = metrics.get("net_profit", 0)
    profit_factor = metrics.get("profit_factor", 0)

    if net_profit > 0 and profit_factor >= 1.5:
        opening = (
            "You completed a profitable week with a healthy trading edge."
        )
    elif net_profit > 0:
        opening = (
            "You finished the week profitably, but your edge still needs "
            "stronger consistency."
        )
    else:
        opening = (
            "You finished the week at a loss, so execution quality and "
            "capital protection must become the priority."
        )

    behavior_note = ""

    if behavior.get("revenge_trading"):
        behavior_note = (
            " Revenge trading was detected and may have increased losses."
        )
    elif behavior.get("fomo_detected"):
        behavior_note = (
            " FOMO entries were detected and reduced entry quality."
        )

    return (
        f"{opening} You completed {total} trades with a "
        f"{win_rate}% win rate and a profit factor of "
        f"{profit_factor}.{behavior_note}"
    )
