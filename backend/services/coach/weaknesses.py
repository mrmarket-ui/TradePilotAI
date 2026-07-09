def identify_weaknesses(analysis: dict) -> list[str]:
    """
    Identify the trader's biggest weaknesses.
    """

    weaknesses = []

    # ----------------------------------
    # Risk
    # ----------------------------------

    risk = analysis.get("risk", {})

    if risk.get("maximum_drawdown", 0) > 1000:
        weaknesses.append("High Drawdown")

    if risk.get("recovery_factor", 2) < 1:
        weaknesses.append("Poor Recovery")

    if risk.get("expectancy", 1) < 0:
        weaknesses.append("Negative Expectancy")

    # ----------------------------------
    # Psychology
    # ----------------------------------

    psychology = analysis.get("psychology", {})

    if psychology.get("discipline_score", 100) < 60:
        weaknesses.append("Low Discipline")

    if psychology.get("confidence_score", 100) < 50:
        weaknesses.append("Low Confidence")

    if psychology.get("stress_score", 0) > 70:
        weaknesses.append("High Stress")

    if psychology.get("greed_score", 0) > 70:
        weaknesses.append("Greed")

    if psychology.get("fear_score", 0) > 70:
        weaknesses.append("Fear")

    # ----------------------------------
    # Behavior
    # ----------------------------------

    behavior = analysis.get("behavior", {})

    if behavior.get("revenge_trading"):
        weaknesses.append("Revenge Trading")

    if behavior.get("fomo_detected"):
        weaknesses.append("FOMO Trading")

    if behavior.get("holding_losers_too_long"):
        weaknesses.append("Holding Losers Too Long")

    if behavior.get("cutting_winners_too_early"):
        weaknesses.append("Cutting Winners Too Early")

    if not behavior.get("position_size_discipline", True):
        weaknesses.append("Poor Position Sizing")

    if not behavior.get("strategy_discipline", True):
        weaknesses.append("Poor Strategy Discipline")

    if not behavior.get("session_discipline", True):
        weaknesses.append("Poor Session Discipline")

    if behavior.get("weekend_trading"):
        weaknesses.append("Weekend Trading")

    # ----------------------------------
    # Performance
    # ----------------------------------

    performance = analysis.get("performance", {})

    if performance.get("win_rate", 100) < 50:
        weaknesses.append("Low Win Rate")

    if performance.get("profit_factor", 2) < 1:
        weaknesses.append("Weak Trading Edge")

    if performance.get("monthly_growth", 0) < 0:
        weaknesses.append("Negative Monthly Growth")

    # ----------------------------------
    # Consistency
    # ----------------------------------

    consistency = analysis.get("consistency", {})

    overall = (
        consistency
        .get("score", {})
        .get("overall_score", 100)
    )

    if overall < 70:
        weaknesses.append("Low Consistency")

    # ----------------------------------
    # Worst Session
    # ----------------------------------

    sessions = consistency.get("sessions", {})

    if sessions:

        worst_session = min(
            sessions,
            key=lambda x: sessions[x].get("win_rate", 100)
        )

        weaknesses.append(
            f"Weakest Session: {worst_session}"
        )

    # ----------------------------------
    # Worst Symbol
    # ----------------------------------

    symbols = consistency.get("symbols", {})

    if symbols:

        worst_symbol = min(
            symbols,
            key=lambda x: symbols[x].get("profit", 999999)
        )

        weaknesses.append(
            f"Weakest Market: {worst_symbol}"
        )

    # ----------------------------------
    # Worst Strategy
    # ----------------------------------

    strategies = consistency.get("strategies", {})

    if strategies:

        worst_strategy = min(
            strategies,
            key=lambda x: strategies[x].get("profit", 999999)
        )

        weaknesses.append(
            f"Weakest Strategy: {worst_strategy}"
        )

    return weaknesses
