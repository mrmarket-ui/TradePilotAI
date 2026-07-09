from services.analytics.risk import analyze_risk
from services.analytics.performance import analyze_performance
from services.consistency.engine import analyze_consistency
from services.behavior.engine import analyze_behavior
from services.psychology.engine import analyze_psychology


def build_analysis(trades):
    """
    Central analysis pipeline.

    Every AI feature should call THIS function instead of
    calling individual engines.
    """

    risk = analyze_risk(trades)

    performance = analyze_performance(trades)

    consistency = analyze_consistency(trades)

    behavior = analyze_behavior(trades)

    psychology = analyze_psychology(trades)

    return {

        "risk": risk,

        "performance": performance,

        "consistency": consistency,

        "behavior": behavior,

        "psychology": psychology

    }
