"""
TradePilot AI
Behavior Analysis Engine
"""

from collections import Counter


def analyze_behavior(trades):

    return {

        "score": calculate_behavior_score(trades),

        "overtrading": detect_overtrading(trades),

        "revenge_trading": detect_revenge_trading(trades),

        "fomo": detect_fomo(trades),

        "holding_losers": detect_holding_losers(trades),

        "cutting_winners": detect_cutting_winners(trades),

        "position_size": detect_position_sizing(trades),

        "strategy_discipline": detect_strategy_discipline(trades),

        "session_discipline": detect_session_discipline(trades),

        "weekend_trading": detect_weekend_trading(trades),

    }


def calculate_behavior_score(trades):

    score = 100

    if detect_overtrading(trades)["detected"]:
        score -= 15

    if detect_revenge_trading(trades)["detected"]:
        score -= 20

    if detect_fomo(trades)["detected"]:
        score -= 15

    if detect_holding_losers(trades)["detected"]:
        score -= 15

    if detect_cutting_winners(trades)["detected"]:
        score -= 10

    if detect_position_sizing(trades)["detected"]:
        score -= 10

    if detect_strategy_discipline(trades)["detected"]:
        score -= 5

    if detect_weekend_trading(trades)["detected"]:
        score -= 5

    return {
        "score": max(score, 0)
    }


def detect_overtrading(trades):

    if not trades:

        return {
            "detected": False,
            "average_trades_per_day": 0
        }

    days = {}

    for trade in trades:

        if trade.opened_at is None:
            continue

        day = trade.opened_at.date()

        days.setdefault(day, 0)

        days[day] += 1

    avg = sum(days.values()) / len(days)

    return {

        "detected": avg > 8,

        "average_trades_per_day": round(avg, 2)

    }


def detect_revenge_trading(trades):

    trades = sorted(

        [t for t in trades if t.closed_at],

        key=lambda x: x.closed_at

    )

    revenge = 0

    for i in range(len(trades)-1):

        current = trades[i]

        nxt = trades[i+1]

        if (

            current.profit < 0

            and

            (nxt.opened_at-current.closed_at).total_seconds() < 900

        ):

            revenge += 1

    return {

        "detected": revenge >= 3,

        "occurrences": revenge

    }

# ==========================================================
# FOMO Detection
# ==========================================================

def detect_fomo(trades):

    fomo = 0

    for trade in trades:

        if (
            trade.entry is not None
            and trade.take_profit is not None
            and trade.stop_loss is not None
        ):

            risk = abs(trade.entry - trade.stop_loss)
            reward = abs(trade.take_profit - trade.entry)

            if risk > 0 and (reward / risk) < 1:
                fomo += 1

    return {
        "detected": fomo >= 3,
        "occurrences": fomo
    }


# ==========================================================
# Holding Losers Too Long
# ==========================================================

def detect_holding_losers(trades):

    count = 0

    for trade in trades:

        if (
            trade.profit is not None
            and trade.profit < 0
            and trade.opened_at
            and trade.closed_at
        ):

            hours = (
                trade.closed_at - trade.opened_at
            ).total_seconds() / 3600

            if hours > 24:
                count += 1

    return {
        "detected": count >= 3,
        "occurrences": count
    }


# ==========================================================
# Cutting Winners Too Early
# ==========================================================

def detect_cutting_winners(trades):

    count = 0

    for trade in trades:

        if (
            trade.profit is not None
            and trade.profit > 0
            and trade.entry is not None
            and trade.take_profit is not None
        ):

            target = abs(
                trade.take_profit - trade.entry
            )

            if target > 0:

                captured = abs(trade.profit)

                if captured < target * 0.5:
                    count += 1

    return {
        "detected": count >= 3,
        "occurrences": count
    }


# ==========================================================
# Position Size Discipline
# ==========================================================

def detect_position_sizing(trades):

    lots = []

    for trade in trades:

        if trade.lot_size:
            lots.append(trade.lot_size)

    if len(lots) < 2:

        return {
            "detected": False,
            "variance": 0
        }

    variance = max(lots) - min(lots)

    return {
        "detected": variance > 2,
        "variance": round(variance, 2)
    }


# ==========================================================
# Strategy Discipline
# ==========================================================

def detect_strategy_discipline(trades):

    strategies = [
        t.strategy
        for t in trades
        if t.strategy
    ]

    if not strategies:

        return {
            "detected": False,
            "strategies_used": 0
        }

    unique = len(set(strategies))

    return {
        "detected": unique > 5,
        "strategies_used": unique
    }


# ==========================================================
# Session Discipline
# ==========================================================

def detect_session_discipline(trades):

    sessions = {
        "Asian": 0,
        "London": 0,
        "New York": 0,
        "Other": 0,
    }

    for trade in trades:

        if not trade.opened_at:
            continue

        hour = trade.opened_at.hour

        if 0 <= hour < 8:
            sessions["Asian"] += 1

        elif 8 <= hour < 16:
            sessions["London"] += 1

        elif 16 <= hour < 22:
            sessions["New York"] += 1

        else:
            sessions["Other"] += 1

    best = max(
        sessions,
        key=sessions.get
    )

    return {
        "best_session": best,
        "distribution": sessions
    }


# ==========================================================
# Weekend Trading
# ==========================================================

def detect_weekend_trading(trades):

    weekends = 0

    for trade in trades:

        if trade.opened_at:

            if trade.opened_at.weekday() >= 5:
                weekends += 1

    return {
        "detected": weekends > 0,
        "weekend_trades": weekends
    }

