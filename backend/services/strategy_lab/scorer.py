from models.strategy_profile import (
    StrategyProfile,
)

from schemas.strategy_profile import (
    SetupScoreRequest,
    SetupScoreResponse,
)


def normalize_values(
    values: list[str],
) -> set[str]:
    return {
        value.strip().lower()
        for value in values
        if value.strip()
    }


def score_setup(
    strategy: StrategyProfile,
    payload: SetupScoreRequest,
) -> SetupScoreResponse:
    required_rules = normalize_values(
        strategy.entry_rules or []
    )

    observed_rules = normalize_values(
        payload.observed_entry_rules
    )

    required_confirmations = normalize_values(
        strategy.confirmations or []
    )

    observed_confirmations = normalize_values(
        payload.observed_confirmations
    )

    matched_rules = (
        required_rules
        & observed_rules
    )

    missing_rules = (
        required_rules
        - observed_rules
    )

    matched_confirmations = (
        required_confirmations
        & observed_confirmations
    )

    missing_confirmations = (
        required_confirmations
        - observed_confirmations
    )

    rule_score = (
        len(matched_rules)
        / max(len(required_rules), 1)
    ) * 55

    confirmation_score = (
        len(matched_confirmations)
        / max(
            len(required_confirmations),
            1,
        )
    ) * 25

    market_passed = (
        not strategy.markets
        or payload.market.strip().lower()
        in normalize_values(strategy.markets)
    )

    session_passed = (
        not strategy.sessions
        or payload.session is None
        or payload.session.strip().lower()
        in normalize_values(strategy.sessions)
    )

    timeframe_passed = (
        not strategy.timeframes
        or payload.timeframe is None
        or payload.timeframe.strip().lower()
        in normalize_values(strategy.timeframes)
    )

    context_score = 0

    if market_passed:
        context_score += 7

    if session_passed:
        context_score += 4

    if timeframe_passed:
        context_score += 4

    risk_passed = (
        payload.risk_percent
        <= strategy.max_risk_percent
    )

    if risk_passed:
        context_score += 5

    daily_limit_passed = (
        payload.trades_today
        < strategy.max_trades_per_day
    )

    consecutive_loss_passed = (
        payload.consecutive_losses
        < strategy.max_consecutive_losses
    )

    psychology_passed = (
        daily_limit_passed
        and consecutive_loss_passed
    )

    overall_score = round(
        min(
            rule_score
            + confirmation_score
            + context_score,
            100,
        ),
        2,
    )

    if not risk_passed:
        verdict = "Excessive risk"

    elif not psychology_passed:
        verdict = "Strategy violation"

    elif missing_confirmations:
        verdict = "Missing confirmation"

    elif overall_score >= 85:
        verdict = "Valid setup"

    elif overall_score >= 65:
        verdict = "Watchlist"

    else:
        verdict = "No trade"

    explanation = [
        (
            f"{len(matched_rules)} of "
            f"{len(required_rules)} entry rules matched."
        ),
        (
            f"{len(matched_confirmations)} of "
            f"{len(required_confirmations)} "
            "confirmations matched."
        ),
    ]

    if not market_passed:
        explanation.append(
            "Market is outside the saved strategy."
        )

    if not session_passed:
        explanation.append(
            "Session is outside the saved strategy."
        )

    if not timeframe_passed:
        explanation.append(
            "Timeframe is outside the saved strategy."
        )

    if not risk_passed:
        explanation.append(
            "Risk exceeds the strategy maximum."
        )

    if not daily_limit_passed:
        explanation.append(
            "Maximum trades per day reached."
        )

    if not consecutive_loss_passed:
        explanation.append(
            "Maximum consecutive-loss limit reached."
        )

    return SetupScoreResponse(
        strategy_id=strategy.id,
        strategy_name=strategy.name,
        overall_score=overall_score,
        verdict=verdict,
        matched_rules=sorted(
            matched_rules
        ),
        missing_rules=sorted(
            missing_rules
        ),
        matched_confirmations=sorted(
            matched_confirmations
        ),
        missing_confirmations=sorted(
            missing_confirmations
        ),
        risk_passed=risk_passed,
        psychology_passed=psychology_passed,
        daily_limit_passed=daily_limit_passed,
        explanation=" ".join(explanation),
    )
