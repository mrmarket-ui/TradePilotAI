from services.trader_dna.engine import (
    analyze_trader_dna,
)

statistics = {
    "win_rate": 68,
}

risk = {
    "risk_score": 82,
}

consistency = {
    "score": 90,
}

psychology = {

    "confidence_score": 88,

    "discipline_score": 92,

    "emotional_control": 90,

    "stress_score": 20,

    "greed_score": 10,

    "fear_score": 15,

}

behavior = {

    "revenge_trading": False,

    "fomo_detected": False,

    "holding_losers_too_long": False,

    "cutting_winners_too_early": True,

    "position_size_discipline": True,

    "strategy_discipline": True,

    "session_discipline": True,

}

print(

    analyze_trader_dna(

        statistics,

        risk,

        consistency,

        psychology,

        behavior,

    )

)