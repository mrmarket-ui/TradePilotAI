def calculate_trade_score(trade):

    score = 100

    if trade.stop_loss <= 0:
        score -= 30

    if trade.take_profit <= trade.entry:
        score -= 25

    if trade.notes is None or trade.notes == "":
        score -= 5

    if trade.emotion:
        emotion = trade.emotion.lower()

        if emotion in [
            "fear",
            "revenge",
            "greed",
            "panic"
        ]:
            score -= 15

        if emotion in [
            "patient",
            "calm",
            "confident"
        ]:
            score += 5

    return max(0, min(score, 100))