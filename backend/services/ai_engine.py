from models.trade import Trade


def analyze_trade(trade: Trade):

    score = 100

    feedback = []

    # Risk Reward
    risk = abs(trade.entry - trade.stop_loss)
    reward = abs(trade.take_profit - trade.entry)

    if risk > 0:
        rr = reward / risk
    else:
        rr = 0

    if rr < 2:
        score -= 15
        feedback.append(
            "Risk-to-reward ratio is below 2:1."
        )
    else:
        feedback.append(
            "Excellent risk-to-reward ratio."
        )

    # Stop Loss Check
    if trade.stop_loss == trade.entry:
        score -= 20
        feedback.append(
            "Stop loss cannot equal entry."
        )

    # Take Profit Check
    if trade.take_profit == trade.entry:
        score -= 20
        feedback.append(
            "Take profit cannot equal entry."
        )

    return {
        "score": score,
        "feedback": feedback
    }