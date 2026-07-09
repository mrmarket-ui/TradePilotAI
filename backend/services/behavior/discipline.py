from collections import Counter


def analyze_position_size(trades):
    """
    Checks whether the trader uses
    reasonably consistent lot sizes.
    """

    lots = []

    for trade in trades:

        lot = getattr(trade, "lot_size", None)

        if lot is None:
            lot = getattr(trade, "volume", None)

        if lot is not None:
            lots.append(float(lot))

    if len(lots) < 5:
        return True

    average = sum(lots) / len(lots)

    tolerance = average * 0.30

    consistent = 0

    for lot in lots:

        if abs(lot - average) <= tolerance:
            consistent += 1

    return consistent / len(lots) >= 0.70


def analyze_strategy_discipline(trades):
    """
    Detects whether one strategy
    is consistently followed.
    """

    names = []

    for trade in trades:

        strategy = getattr(trade, "strategy", None)

        if strategy:
            names.append(strategy)

    if len(names) < 5:
        return True

    most_common = Counter(names).most_common(1)[0][1]

    return most_common / len(names) >= 0.60


def analyze_session_discipline(trades):
    """
    Detects whether most trades
    happen during one preferred session.
    """

    sessions = []

    for trade in trades:

        if not trade.opened_at:
            continue

        hour = trade.opened_at.hour

        if hour < 8:
            sessions.append("asian")

        elif hour < 16:
            sessions.append("london")

        else:
            sessions.append("new_york")

    if len(sessions) < 5:
        return True

    dominant = Counter(sessions).most_common(1)[0][1]

    return dominant / len(sessions) >= 0.60