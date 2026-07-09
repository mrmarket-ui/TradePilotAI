from services.consistency.engine import (
    analyze_consistency as consistency_engine
)


def analyze_consistency(trades):

    return consistency_engine(trades)
