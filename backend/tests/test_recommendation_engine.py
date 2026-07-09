from services.recommendations.engine import (
    generate_recommendations
)

risk = {
    "maximum_drawdown": 1200,
    "recovery_factor": 0.8,
    "expectancy": -15,
}

behavior = {
    "revenge_trading": True,
    "fomo_detected": True,
    "holding_losers_too_long": True,
    "cutting_winners_too_early": False,
    "position_size_discipline": False,
    "strategy_discipline": True,
    "session_discipline": True,
    "weekend_trading": False,
}

psychology = {
    "confidence_score": 45,
    "discipline_score": 55,
    "emotional_control": 50,
    "greed_score": 80,
    "fear_score": 40,
    "stress_score": 90,
}

consistency = {
    "score": {
        "overall_score": 78
    },
    "trend": "Improving",
    "sessions": {
        "London": {
            "win_rate": 75
        }
    },
    "weekdays": {
        "Tuesday": {
            "win_rate": 72
        }
    },
    "symbols": {
        "XAUUSD": {
            "profit": 3500
        }
    },
    "strategies": {
        "Liquidity Sweep": {
            "profit": 4800
        }
    },
}

strategies = {
    "Liquidity Sweep": {
        "profit": 4800
    },
    "Breakout": {
        "profit": -500
    },
}

performance = {
    "trend": "Improving",
    "monthly_growth": 18,
    "win_rate": 67,
    "profit_factor": 1.8,
    "consistency_score": 78,
}

recommendations = generate_recommendations(
    risk,
    behavior,
    psychology,
    consistency,
    strategies,
    performance,
)

print("=" * 60)

for recommendation in recommendations:

    print(
        f"[{recommendation['priority']}] "
        f"{recommendation['category']} - "
        f"{recommendation['title']}"
    )

print("=" * 60)
print("TOTAL:", len(recommendations))