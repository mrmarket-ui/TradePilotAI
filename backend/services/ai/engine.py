from services.ai.risk import analyze_risk
from services.ai.behavior import analyze_behavior
from services.ai.psychology import analyze_psychology
from services.ai.consistency import analyze_consistency
from services.ai.strategy import analyze_strategy
from services.ai.performance import analyze_performance


def analyze_trader(trades):

    return {

        "risk":
            analyze_risk(trades),

        "behavior":
            analyze_behavior(trades),

        "psychology":
            analyze_psychology(trades),

        "consistency":
            analyze_consistency(trades),

        "strategies":
            analyze_strategy(trades),

        "performance":
            analyze_performance(trades),

    }
