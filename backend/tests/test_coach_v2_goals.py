from services.coach.v2.goals import generate_goals

analysis = {

    "risk": {
        "expectancy": -2,
    },

    "behavior": {
        "revenge_trading": True,
        "fomo_detected": False,
    },

    "performance": {
        "profit_factor": 0.32,
    }

}

print(generate_goals(analysis))
