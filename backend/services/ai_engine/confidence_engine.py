class ConfidenceEngine:

    @staticmethod
    def score(analysis):

        score = 50

        if analysis["trend"] == "Bullish":
            score += 20

        if analysis["momentum"] == "Strong":
            score += 20

        if analysis["volatility"] == "Medium":
            score += 10

        return min(score, 100)