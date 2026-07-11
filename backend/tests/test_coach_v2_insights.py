from services.coach.v2.insights import generate_insights

analysis = {

    "risk": {
        "expectancy": -2,
    },

    "behavior": {
        "revenge_trading": True,
    },

    "psychology": {
        "discipline_score": 80,
        "confidence_score": 57,
    },

    "performance": {
        "profit_factor": 0.32,
    },

    "consistency": {
        "score": {
            "overall_score": 23,
        }
    },

    "trader_dna": {

        "profile":"Emotional Trader",

        "overall_score":54,

        "strengths":[
            "Consistent position sizing"
        ],

        "weaknesses":[
            "Revenge trading"
        ]

    }

}

print(generate_insights(analysis))
