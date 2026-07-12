from pprint import pprint

from services.ai_chat.engine import generate_chat_reply

context = {

    "performance":{
        "win_rate":16.67,
        "profit_factor":0.32
    },

    "behavior":{
        "revenge_trading":True
    },

    "psychology":{
        "discipline_score":80,
        "confidence_score":57
    },

    "trader_dna":{
        "profile":"Emotional Trader"
    }

}

pprint(
    generate_chat_reply(
        "Why am I losing money?",
        context,
    )
)

print()

pprint(
    generate_chat_reply(
        "Tell me about my psychology",
        context,
    )
)

print()

pprint(
    generate_chat_reply(
        "What is my trader DNA?",
        context,
    )
)
