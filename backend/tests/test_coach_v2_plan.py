from services.coach.v2.plan import generate_improvement_plan

analysis = {

    "behavior": {
        "revenge_trading": True,
        "fomo_detected": False,
    },

    "risk": {
        "expectancy": -2,
    },

    "performance": {
        "profit_factor": 0.32,
    }

}

from pprint import pprint

pprint(
    generate_improvement_plan(
        analysis
    )
)
