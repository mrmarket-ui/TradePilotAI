PLAN_MAP = {
    "High Drawdown": [
        "Reduce risk to a maximum of 1% per trade.",
        "Stop trading after two consecutive losses.",
        "Review every losing trade before taking another position."
    ],

    "Poor Recovery": [
        "Focus on capital preservation this week.",
        "Avoid increasing position size after losses.",
        "Only trade A+ setups."
    ],

    "Negative Expectancy": [
        "Review your trading strategy before your next session.",
        "Avoid impulsive trades.",
        "Take only setups that meet every rule."
    ],

    "Revenge Trading": [
        "Take a 30-minute break after every losing trade.",
        "Set a daily loss limit.",
        "Never try to win back losses immediately."
    ],

    "FOMO Trading": [
        "Wait for candle confirmation.",
        "Avoid chasing missed entries.",
        "Accept that opportunities come every day."
    ],

    "Holding Losers Too Long": [
        "Respect every stop loss.",
        "Never move your stop further away.",
        "Accept small losses as business expenses."
    ],

    "Cutting Winners Too Early": [
        "Follow your take-profit plan.",
        "Allow winners enough room to develop.",
        "Avoid closing trades because of fear."
    ],

    "Poor Position Sizing": [
        "Use a fixed percentage risk per trade.",
        "Never increase lot size emotionally.",
        "Calculate risk before entering every trade."
    ],

    "Poor Strategy Discipline": [
        "Trade only your primary strategy today.",
        "Ignore setups outside your checklist.",
        "Review your strategy before the session starts."
    ],

    "Poor Session Discipline": [
        "Trade only during your best-performing session.",
        "Avoid low-liquidity hours.",
        "Stick to your trading schedule."
    ],

    "Weekend Trading": [
        "Avoid opening new trades over the weekend.",
        "Use weekends for review and planning.",
        "Prepare your watchlist before Monday."
    ],

    "Low Discipline": [
        "Follow every rule in your trading plan.",
        "Journal every completed trade.",
        "Review your execution after the session."
    ],

    "Low Confidence": [
        "Trade smaller position sizes today.",
        "Trust your proven trading plan.",
        "Avoid changing your strategy mid-session."
    ],

    "High Stress": [
        "Reduce the number of trades today.",
        "Take breaks between trades.",
        "Avoid trading when emotionally overwhelmed."
    ],

    "Greed": [
        "Set a daily profit target.",
        "Stop trading after reaching your target.",
        "Do not overtrade."
    ],

    "Fear": [
        "Execute only confirmed setups.",
        "Accept normal trading risk.",
        "Trust your trading process."
    ],

    "Low Win Rate": [
        "Take fewer but higher-quality trades.",
        "Review your losing trades this evening.",
        "Avoid forcing opportunities."
    ],

    "Weak Trading Edge": [
        "Backtest your strategy this week.",
        "Remove low-probability setups.",
        "Focus on your strongest market."
    ],

    "Negative Monthly Growth": [
        "Prioritize consistency over recovery.",
        "Reduce trading frequency.",
        "Review your monthly journal."
    ],

    "Low Consistency": [
        "Trade at the same time every day.",
        "Follow one routine.",
        "Journal every session."
    ]
}


def generate_action_plan(weaknesses: list[str]) -> list[str]:
    """
    Generate a personalized action plan based on detected weaknesses.
    """

    plan = []

    for weakness in weaknesses:

        if weakness.startswith("Weakest"):
            continue

        actions = PLAN_MAP.get(weakness)

        if actions:

            for action in actions:

                if action not in plan:
                    plan.append(action)

        if len(plan) >= 5:
            break

    if not plan:

        plan = [
            "Continue following your trading plan.",
            "Maintain consistent risk management.",
            "Journal every completed trade."
        ]

    return plan[:5]
