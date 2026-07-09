from services.psychology.confidence import (
    calculate_confidence_score,
)

from services.psychology.discipline import (
    calculate_discipline_score,
)

from services.psychology.emotion import (
    calculate_emotional_scores,
)

from services.psychology.stress import (
    calculate_stress_score,
)


def analyze_psychology(
    trades,
    behavior,
    consistency_trend="stable",
):
    """
    Builds the trader's psychological profile
    from trade history and behavior.
    """

    confidence = calculate_confidence_score(
        trades,
        consistency_trend,
    )

    discipline = calculate_discipline_score(
        behavior
    )

    emotion = calculate_emotional_scores(
        behavior
    )

    stress = calculate_stress_score(
        behavior
    )

    return {

        "confidence_score": confidence,

        "discipline_score": discipline,

        "stress_score": stress,

        **emotion,

    }