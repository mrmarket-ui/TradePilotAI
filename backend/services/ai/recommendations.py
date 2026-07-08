def generate_recommendations(stats, risk):

    recommendations = []

    if stats["win_rate"] < 50:

        recommendations.append(
            "Focus on improving your entry confirmation before opening trades."
        )

    if risk["maximum_drawdown"] > 10:

        recommendations.append(
            "Reduce your position size to lower maximum drawdown."
        )

    if risk["expectancy"] < 0:

        recommendations.append(
            "Your trading expectancy is negative. Review losing setups."
        )

    if risk["average_risk_reward"] < 2:

        recommendations.append(
            "Aim for trades with at least a 1:2 risk-to-reward ratio."
        )

    if not recommendations:

        recommendations.append(
            "Excellent work. Keep following your trading plan."
        )

    return recommendations
