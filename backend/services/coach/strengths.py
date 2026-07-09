def identify_strengths(analysis: dict) -> list[str]:
    """
    Identify the trader's strongest habits and performance.
    """

    strengths = []

    # ----------------------------------
    # Risk
    # ----------------------------------

    risk = analysis.get("risk", {})

    if risk.get("maximum_drawdown", 999999) < 500:
        strengths.append("Excellent Risk Management")

    if risk.get("recovery_factor", 0) >= 2:
        strengths.append("Strong Recovery Ability")

    if risk.get("expectancy", -1) > 0:
        strengths.append("Positive Trading Expectancy")

    # ----------------------------------
    # Psychology
    # ----------------------------------

    psychology = analysis.get("psychology", {})

    if psychology.get("discipline_score", 0) >= 80:
        strengths.append("Highly Disciplined")

    if psychology.get("confidence_score", 0) >= 80:
        strengths.append("Strong Trading Confidence")

    if psychology.get("emotional_control", 0) >= 80:
        strengths.append("Excellent Emotional Control")

    if psychology.get("stress_score", 100) <= 30:
        strengths.append("Handles Stress Well")

    # ----------------------------------
    # Behavior
    # ----------------------------------

    behavior = analysis.get("behavior", {})

    if not behavior.get("revenge_trading", False):
        strengths.append("Avoids Revenge Trading")

    if not behavior.get("fomo_detected", False):
        strengths.append("Patient Trade Execution")

    if behavior.get("position_size_discipline", False):
        strengths.append("Consistent Position Sizing")

    # ----------------------------------
    # Performance
    # ----------------------------------

    performance = analysis.get("performance", {})

    if performance.get("win_rate", 0) >= 60:
        strengths.append("High Win Rate")

    if performance.get("profit_factor", 0) >= 1.5:
        strengths.append("Strong Trading Edge")

    if performance.get("monthly_growth", 0) > 0:
        strengths.append("Consistent Monthly Growth")

    # ----------------------------------
    # Consistency
    # ----------------------------------

    consistency = analysis.get("consistency", {})

    overall = (
        consistency
        .get("score", {})
        .get("overall_score", 0)
    )

    if overall >= 85:
        strengths.append("Highly Consistent Trader")

    # ----------------------------------
    # Best Session
    # ----------------------------------

    sessions = consistency.get("sessions", {})

    if sessions:

        best_session = max(
            sessions,
            key=lambda x: sessions[x].get("win_rate", 0)
        )

        strengths.append(
            f"Best Session: {best_session}"
        )

    # ----------------------------------
    # Best Symbol
    # ----------------------------------

    symbols = consistency.get("symbols", {})

    if symbols:

        best_symbol = max(
            symbols,
            key=lambda x: symbols[x].get("profit", 0)
        )

        strengths.append(
            f"Best Market: {best_symbol}"
        )

    # ----------------------------------
    # Best Strategy
    # ----------------------------------

    strategies = consistency.get("strategies", {})

    if strategies:

        best_strategy = max(
            strategies,
            key=lambda x: strategies[x].get("profit", 0)
        )

        strengths.append(
            f"Best Strategy: {best_strategy}"
        )

    return strengths
