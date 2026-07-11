from services.coach.v2.engine import generate_ai_coach

analysis = {

    "risk":{
        "expectancy":-2
    },

    "behavior":{
        "revenge_trading":True
    },

    "psychology":{
        "discipline_score":80,
        "confidence_score":57,
        "emotional_control":80
    },

    "performance":{
        "profit_factor":0.32,
        "win_rate":16.67
    },

    "consistency":{
        "score":{
            "overall_score":23
        }
    },

    "trader_dna":{
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

from pprint import pprint

pprint(
    generate_ai_coach(
        analysis
    )
)
