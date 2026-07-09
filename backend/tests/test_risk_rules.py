from services.recommendations.risk_rules import (
    generate_risk_recommendations
)

risk = {

    "maximum_drawdown": 1200,

    "recovery_factor": 0.8,

    "expectancy": -15

}

recommendations = generate_risk_recommendations(risk)

for recommendation in recommendations:

    print(recommendation)
