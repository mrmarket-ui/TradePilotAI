def classify_verdict(score: float) -> str:
    if score >= 95:
        return "Elite Setup"

    if score >= 85:
        return "Valid Setup"

    if score >= 70:
        return "Watchlist"

    if score >= 50:
        return "Weak Setup"

    return "Reject"


def build_recommendation(
    score: float,
    weaknesses: list[str],
) -> str:
    if score >= 95:
        return (
            "The setup strongly matches the strategy. "
            "Confirm live market conditions and preserve risk discipline."
        )

    if score >= 85:
        return (
            "The setup is valid, but review the remaining weak points "
            "before entering."
        )

    if score >= 70:
        if weaknesses:
            return (
                "Keep the setup on the watchlist. Resolve: "
                + "; ".join(weaknesses[:3])
            )

        return "Wait for stronger confirmation before entering."

    if score >= 50:
        return (
            "The setup is weak and does not meet enough strategy conditions."
        )

    return (
        "Reject the setup. It violates too many strategy requirements."
    )
