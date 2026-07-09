FOCUS_MAP = {
    "High Drawdown":
        "Reduce your risk per trade and protect your capital.",

    "Poor Recovery":
        "Focus on preserving capital before chasing profits.",

    "Negative Expectancy":
        "Only take setups that match your trading plan.",

    "Revenge Trading":
        "Walk away after a loss. Never trade emotionally.",

    "FOMO Trading":
        "Wait for confirmation before entering a trade.",

    "Holding Losers Too Long":
        "Respect every stop loss today.",

    "Cutting Winners Too Early":
        "Allow winning trades to reach their planned target.",

    "Poor Position Sizing":
        "Risk the same percentage on every trade.",

    "Poor Strategy Discipline":
        "Trade only your primary strategy today.",

    "Poor Session Discipline":
        "Trade only during your highest-performing session.",

    "Weekend Trading":
        "Avoid opening new positions during the weekend.",

    "Low Discipline":
        "Follow your trading rules without exception today.",

    "Low Confidence":
        "Trust your tested strategy and avoid hesitation.",

    "High Stress":
        "Reduce trading frequency and stay patient.",

    "Greed":
        "Don't force extra trades after reaching your target.",

    "Fear":
        "Execute your plan confidently without second-guessing.",

    "Low Win Rate":
        "Focus on quality setups rather than quantity.",

    "Weak Trading Edge":
        "Review your strategy before taking new trades.",

    "Negative Monthly Growth":
        "Prioritize consistency over making back losses quickly.",

    "Low Consistency":
        "Repeat the habits that produced your best trading days."
}


def generate_daily_focus(
    strengths: list[str],
    weaknesses: list[str]
) -> str:
    """
    Generate one clear coaching focus for today.
    """

    if weaknesses:

        for weakness in weaknesses:

            if weakness.startswith("Weakest"):
                continue

            if weakness in FOCUS_MAP:
                return FOCUS_MAP[weakness]

        return (
            "Trade your plan and focus on disciplined execution."
        )

    if strengths:

        return (
            "Keep reinforcing your strengths and execute your plan consistently."
        )

    return (
        "Focus on following your trading plan one trade at a time."
    )
