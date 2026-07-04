from services.ai_engine.market_analyzer import MarketAnalyzer
from services.ai_engine.confidence_engine import ConfidenceEngine


class SignalGenerator:

    @staticmethod
    def generate(data):

        analysis = MarketAnalyzer.analyze(data)

        confidence = ConfidenceEngine.score(
            analysis
        )

        signal = "WAIT"

        if confidence >= 80:
            signal = "BUY"

        if (
            confidence >= 80
            and analysis["trend"] == "Bearish"
        ):
            signal = "SELL"

        return {
            "signal": signal,
            "confidence": confidence,
            "analysis": analysis
        }