from services.coach.v2.summary import generate_summary


analysis = {
    "risk": {
        "expectancy": -2.08,
        "recovery_factor": -0.77,
    },
    "behavior": {
        "revenge_trading": True,
        "fomo_detected": False,
        "holding_losers_too_long": False,
        "cutting_winners_too_early": False,
        "position_size_discipline": True,
    },
    "psychology": {
        "discipline_score": 80,
    },
    "performance": {
        "win_rate": 16.67,
        "profit_factor": 0.32,
    },
    "consistency": {
        "score": {
            "overall_score": 23.03,
        }
    },
    "trader_dna": {
        "profile": "Emotional Trader",
    },
}

print(generate_summary(analysis))
