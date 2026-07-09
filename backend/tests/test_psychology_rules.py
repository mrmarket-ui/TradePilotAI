from services.recommendations.psychology_rules import (
    generate_psychology_recommendations
)

psychology = {

    "confidence_score": 35,

    "discipline_score": 50,

    "emotional_control": 45,

    "greed_score": 80,

    "fear_score": 75,

    "stress_score": 90

}

recommendations = generate_psychology_recommendations(
    psychology
)

for recommendation in recommendations:

    print(recommendation)
