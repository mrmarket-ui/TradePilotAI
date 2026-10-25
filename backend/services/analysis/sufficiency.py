"""
TradePilot AI minimum-data rules.

One place that decides when there is enough completed-trade history to show
grades, strengths and trader profiles. Tune the thresholds here.
"""

from __future__ import annotations

MIN_TRADES_TRADER_DNA = 10
MIN_TRADES_REVIEW = 3

NOT_ENOUGH_DATA = "Not enough data yet"


def insufficient_trader_dna(trades_recorded: int) -> dict:
    return {
        "profile": NOT_ENOUGH_DATA,
        "overall_score": 0.0,
        "personality": [],
        "strengths": [],
        "weaknesses": [],
        "sufficient_data": False,
        "trades_recorded": trades_recorded,
        "trades_needed": max(0, MIN_TRADES_TRADER_DNA - trades_recorded),
    }


def apply_review_gate(review: dict, period: str) -> dict:
    """
    Remove grade, score and invented insights from a weekly or monthly
    review that does not have enough completed trades behind it.
    """
    metrics = review.get("metrics")

    if not isinstance(metrics, dict) or "total_trades" not in metrics:
        return review

    total = int(metrics.get("total_trades") or 0)

    if total >= MIN_TRADES_REVIEW:
        return review

    needed = MIN_TRADES_REVIEW - total

    if total == 0:
        summary = f"No completed trades were recorded this {period}."
    else:
        summary = (
            f"Only {total} completed trade(s) this {period}, which is too "
            "few for a graded review."
        )

    gated = dict(review)
    gated.update(
        {
            "grade": None,
            "score": None,
            "summary": summary,
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "sufficient_data": False,
            "trades_needed": needed,
            f"next_{period}_mission": (
                f"Log at least {MIN_TRADES_REVIEW} completed trades "
                f"this {period} to unlock a graded review."
            ),
        }
    )

    return gated