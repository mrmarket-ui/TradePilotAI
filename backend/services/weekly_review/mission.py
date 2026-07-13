def generate_weekly_mission(
    analysis: dict,
) -> str:
    behavior = analysis.get("behavior", {})
    performance = analysis.get("performance", {})
    risk = analysis.get("risk", {})

    if behavior.get("revenge_trading"):
        return (
            "Complete the next week with zero revenge trades and take "
            "a mandatory break after every loss."
        )

    if behavior.get("fomo_detected"):
        return (
            "Only enter trades that meet your full confirmation checklist."
        )

    if risk.get("expectancy", 0) < 0:
        return (
            "Reduce trade frequency and take only your highest-quality setups."
        )

    if performance.get("profit_factor", 0) < 1:
        return (
            "Focus on protecting capital and improving reward-to-risk quality."
        )

    return (
        "Repeat your best process consistently without increasing risk."
    )
