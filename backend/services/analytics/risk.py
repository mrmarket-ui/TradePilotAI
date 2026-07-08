"""
TradePilot AI
Risk Analytics Engine

Part 1

Core risk calculations used throughout the platform.

Includes:

- Maximum Drawdown
- Win/Loss Streaks
- Recovery Factor
- Expectancy
- Largest Win/Loss

Author: TradePilot AI
"""

from __future__ import annotations

from typing import List

from models.trade import Trade


# ==========================================================
# Helpers
# ==========================================================

def _profit(trade: Trade) -> float:
    """
    Safely return trade profit.
    """

    return float(trade.profit or 0)


def _closed_trades(
    trades: List[Trade]
) -> List[Trade]:
    """
    Return only closed trades sorted by close time.
    """

    return sorted(
        [
            t
            for t in trades
            if t.closed_at is not None
        ],
        key=lambda x: x.closed_at
    )


# ==========================================================
# Maximum Drawdown
# ==========================================================

def calculate_max_drawdown(
    trades: List[Trade]
) -> float:
    """
    Calculates the largest peak-to-valley decline.
    """

    trades = _closed_trades(trades)

    balance = 0.0
    peak = 0.0
    max_drawdown = 0.0

    for trade in trades:

        balance += _profit(trade)

        if balance > peak:
            peak = balance

        drawdown = peak - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return round(max_drawdown, 2)


# ==========================================================
# Consecutive Wins
# ==========================================================

def calculate_consecutive_wins(
    trades: List[Trade]
) -> int:

    trades = _closed_trades(trades)

    current = 0
    longest = 0

    for trade in trades:

        if _profit(trade) > 0:

            current += 1

            if current > longest:
                longest = current

        else:
            current = 0

    return longest


# ==========================================================
# Consecutive Losses
# ==========================================================

def calculate_consecutive_losses(
    trades: List[Trade]
) -> int:

    trades = _closed_trades(trades)

    current = 0
    longest = 0

    for trade in trades:

        if _profit(trade) < 0:

            current += 1

            if current > longest:
                longest = current

        else:
            current = 0

    return longest


# ==========================================================
# Largest Winning Trade
# ==========================================================

def largest_win(
    trades: List[Trade]
) -> float:
    """
    Returns the largest winning trade.
    """

    if not trades:
        return 0

    return round(

        max(
            (_profit(t) for t in trades),
            default=0
        ),

        2
    )


# ==========================================================
# Largest Losing Trade
# ==========================================================

def largest_loss(
    trades: List[Trade]
) -> float:
    """
    Returns the largest losing trade.
    """

    if not trades:
        return 0

    return round(

        min(
            (_profit(t) for t in trades),
            default=0
        ),

        2
    )


# ==========================================================
# Recovery Factor
# ==========================================================

def calculate_recovery_factor(
    trades: List[Trade]
) -> float:
    """
    Recovery Factor =
    Net Profit / Maximum Drawdown
    """

    net_profit = sum(
        _profit(t)
        for t in trades
    )

    drawdown = calculate_max_drawdown(trades)

    if drawdown <= 0:
        return round(net_profit, 2)

    return round(
        net_profit / drawdown,
        2
    )


# ==========================================================
# Expectancy
# ==========================================================

def calculate_expectancy(
    trades: List[Trade]
) -> float:
    """
    Trading Expectancy.

    Formula:

    (Win Rate × Average Win)
        -
    (Loss Rate × Average Loss)
    """

    trades = _closed_trades(trades)

    if not trades:
        return 0

    winners = [
        _profit(t)
        for t in trades
        if _profit(t) > 0
    ]

    losers = [
        abs(_profit(t))
        for t in trades
        if _profit(t) < 0
    ]

    total = len(trades)

    win_rate = len(winners) / total
    loss_rate = len(losers) / total

    average_win = (
        sum(winners) / len(winners)
        if winners else 0
    )

    average_loss = (
        sum(losers) / len(losers)
        if losers else 0
    )

    expectancy = (
        (win_rate * average_win)
        -
        (loss_rate * average_loss)
    )

    return round(expectancy, 2)

# ==========================================================
# Holding Time Analytics
# ==========================================================

def average_holding_hours(
    trades: List[Trade]
) -> float:
    """
    Average duration of all closed trades.
    """

    durations = []

    for trade in trades:

        if trade.opened_at and trade.closed_at:

            hours = (
                trade.closed_at -
                trade.opened_at
            ).total_seconds() / 3600

            durations.append(hours)

    if not durations:
        return 0

    return round(
        sum(durations) / len(durations),
        2
    )


def average_winning_holding_hours(
    trades: List[Trade]
) -> float:
    """
    Average holding time of winning trades.
    """

    durations = []

    for trade in trades:

        if (
            trade.opened_at
            and trade.closed_at
            and _profit(trade) > 0
        ):

            durations.append(

                (
                    trade.closed_at -
                    trade.opened_at
                ).total_seconds() / 3600

            )

    if not durations:
        return 0

    return round(
        sum(durations) / len(durations),
        2
    )


def average_losing_holding_hours(
    trades: List[Trade]
) -> float:
    """
    Average holding time of losing trades.
    """

    durations = []

    for trade in trades:

        if (
            trade.opened_at
            and trade.closed_at
            and _profit(trade) < 0
        ):

            durations.append(

                (
                    trade.closed_at -
                    trade.opened_at
                ).total_seconds() / 3600

            )

    if not durations:
        return 0

    return round(
        sum(durations) / len(durations),
        2
    )


# ==========================================================
# Trading Frequency
# ==========================================================

def average_trades_per_day(
    trades: List[Trade]
) -> float:
    """
    Average trades opened per day.
    """

    opened = [
        t.opened_at
        for t in trades
        if t.opened_at
    ]

    if len(opened) < 2:
        return len(opened)

    first = min(opened)
    last = max(opened)

    days = max(
        (last - first).days,
        1
    )

    return round(
        len(opened) / days,
        2
    )


def average_trades_per_week(
    trades: List[Trade]
) -> float:
    """
    Average trades per week.
    """

    return round(
        average_trades_per_day(trades) * 7,
        2
    )


def average_trades_per_month(
    trades: List[Trade]
) -> float:
    """
    Average trades per month.
    """

    return round(
        average_trades_per_day(trades) * 30,
        2
    )


# ==========================================================
# Trading Session Statistics
# ==========================================================

def session_breakdown(
    trades: List[Trade]
):
    """
    Counts trades by trading session.

    Asian:
        00:00-07:59

    London:
        08:00-15:59

    New York:
        16:00-23:59
    """

    sessions = {
        "asian": 0,
        "london": 0,
        "new_york": 0
    }

    for trade in trades:

        if not trade.opened_at:
            continue

        hour = trade.opened_at.hour

        if hour < 8:
            sessions["asian"] += 1

        elif hour < 16:
            sessions["london"] += 1

        else:
            sessions["new_york"] += 1

    return sessions


# ==========================================================
# Win Rate By Session
# ==========================================================

def win_rate_by_session(
    trades: List[Trade]
):

    data = {
        "asian": [],
        "london": [],
        "new_york": []
    }

    for trade in trades:

        if not trade.opened_at:
            continue

        hour = trade.opened_at.hour

        if hour < 8:
            data["asian"].append(_profit(trade))

        elif hour < 16:
            data["london"].append(_profit(trade))

        else:
            data["new_york"].append(_profit(trade))

    result = {}

    for session, profits in data.items():

        if not profits:

            result[session] = 0

            continue

        wins = len(
            [
                p
                for p in profits
                if p > 0
            ]
        )

        result[session] = round(
            wins / len(profits) * 100,
            2
        )

    return result
# ==========================================================
# Risk / Reward Analytics
# ==========================================================

def calculate_risk_reward(
    trade: Trade
):
    """
    Calculate the planned Risk:Reward ratio.

    Formula:
        Reward / Risk
    """

    if (
        trade.entry is None
        or trade.stop_loss is None
        or trade.take_profit is None
    ):
        return None

    risk = abs(
        trade.entry -
        trade.stop_loss
    )

    reward = abs(
        trade.take_profit -
        trade.entry
    )

    if risk == 0:
        return None

    return reward / risk


def average_risk_reward(
    trades: List[Trade]
):

    ratios = []

    for trade in trades:

        rr = calculate_risk_reward(trade)

        if rr is not None:
            ratios.append(rr)

    if not ratios:
        return 0

    return round(
        sum(ratios) / len(ratios),
        2
    )


def best_risk_reward(
    trades: List[Trade]
):

    ratios = [
        calculate_risk_reward(t)
        for t in trades
    ]

    ratios = [
        r for r in ratios
        if r is not None
    ]

    if not ratios:
        return 0

    return round(
        max(ratios),
        2
    )


def worst_risk_reward(
    trades: List[Trade]
):

    ratios = [
        calculate_risk_reward(t)
        for t in trades
    ]

    ratios = [
        r for r in ratios
        if r is not None
    ]

    if not ratios:
        return 0

    return round(
        min(ratios),
        2
    )


def average_risk(
    trades: List[Trade]
):

    risks = []

    for trade in trades:

        if (
            trade.entry is not None
            and trade.stop_loss is not None
        ):

            risks.append(
                abs(
                    trade.entry -
                    trade.stop_loss
                )
            )

    if not risks:
        return 0

    return round(
        sum(risks) / len(risks),
        5
    )


def average_reward(
    trades: List[Trade]
):

    rewards = []

    for trade in trades:

        if (
            trade.entry is not None
            and trade.take_profit is not None
        ):

            rewards.append(
                abs(
                    trade.take_profit -
                    trade.entry
                )
            )

    if not rewards:
        return 0

    return round(
        sum(rewards) / len(rewards),
        5
    )


# ==========================================================
# Professional Trading Score
# ==========================================================

def risk_score(
    trades: List[Trade]
):
    """
    Returns a score out of 100 based on
    average Risk:Reward.
    """

    rr = average_risk_reward(trades)

    score = min(
        rr / 3,
        1
    ) * 100

    return round(score, 1)


def trade_quality_score(
    trades: List[Trade]
):
    """
    Combines:

    • Win Rate
    • Risk Reward
    • Recovery Factor

    into one professional score.
    """

    if not trades:
        return 0

    wins = len(
        [
            t
            for t in trades
            if _profit(t) > 0
        ]
    )

    win_rate = wins / len(trades)

    rr = average_risk_reward(trades)

    recovery = calculate_recovery_factor(trades)

    score = (

        (win_rate * 40)

        +

        (min(rr / 3, 1) * 35)

        +

        (min(recovery / 5, 1) * 25)

    ) * 100 / 100

    return round(score, 1)


# ==========================================================
# Risk Classification
# ==========================================================

def classify_risk(
    trades: List[Trade]
):

    rr = average_risk_reward(trades)

    if rr >= 3:
        return "Excellent"

    if rr >= 2:
        return "Good"

    if rr >= 1.5:
        return "Average"

    if rr >= 1:
        return "Poor"

    return "Very Poor"


# ==========================================================
# Dashboard Summary
# ==========================================================

def build_risk_summary(
    trades: List[Trade]
):

    return {

        "maximum_drawdown":
            calculate_max_drawdown(trades),

        "recovery_factor":
            calculate_recovery_factor(trades),

        "expectancy":
            calculate_expectancy(trades),

        "largest_win":
            largest_win(trades),

        "largest_loss":
            largest_loss(trades),

        "average_holding_hours":
            average_holding_hours(trades),

        "average_winning_holding_hours":
            average_winning_holding_hours(trades),

        "average_losing_holding_hours":
            average_losing_holding_hours(trades),

        "average_risk_reward":
            average_risk_reward(trades),

        "best_risk_reward":
            best_risk_reward(trades),

        "worst_risk_reward":
            worst_risk_reward(trades),

        "average_risk":
            average_risk(trades),

        "average_reward":
            average_reward(trades),

        "risk_score":
            risk_score(trades),

        "trade_quality_score":
            trade_quality_score(trades),

        "risk_classification":
            classify_risk(trades),

        "longest_win_streak":
            calculate_consecutive_wins(trades),

        "longest_loss_streak":
            calculate_consecutive_losses(trades),

        "average_trades_per_day":
            average_trades_per_day(trades),

        "average_trades_per_week":
            average_trades_per_week(trades),

        "average_trades_per_month":
            average_trades_per_month(trades),

        "session_breakdown":
            session_breakdown(trades),

        "session_win_rate":
            win_rate_by_session(trades)
    }