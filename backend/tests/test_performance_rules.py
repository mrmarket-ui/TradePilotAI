from services.recommendations.performance_rules import (
    generate_performance_recommendations
)

performance = {

    "trend":"Improving",

    "monthly_growth":32,

    "win_rate":76,

    "profit_factor":2.4,

    "consistency_score":91

}

recommendations = generate_performance_recommendations(
    performance
)

for recommendation in recommendations:

    print(recommendation)
