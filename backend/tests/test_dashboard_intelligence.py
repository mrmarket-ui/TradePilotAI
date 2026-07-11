from pprint import pprint

from services.dashboard.intelligence.engine import (
    generate_dashboard_intelligence,
)

analysis = {
    "risk": {
        "expectancy": -2.08,
        "maximum_drawdown": 16.2,
        "recovery_factor": -0.77,
    },
    "behavior": {
        "revenge_trading": True,
        "fomo_detected": False,
    },
    "psychology": {
        "discipline_score": 80,
        "emotional_control": 80,
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
        "overall_score": 54.1,
    },
    "recommendations": [
        {
            "priority": "Critical",
            "category": "Behavior",
            "title": "Stop Revenge Trading",
            "message": "Take a break after losing trades.",
        }
    ],
}

pprint(
    generate_dashboard_intelligence(
        analysis
    )
)
