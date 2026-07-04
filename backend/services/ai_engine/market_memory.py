from collections import Counter


class MarketMemory:

    @staticmethod
    def summarize(trades):

        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "favorite_pair": None,
                "favorite_strategy": None,
                "average_profit": 0
            }

        wins = [
            t for t in trades
            if t.profit is not None and t.profit > 0
        ]

        pairs = Counter(t.pair for t in trades)

        strategies = Counter(
            t.strategy
            for t in trades
            if t.strategy
        )

        profits = [
            t.profit
            for t in trades
            if t.profit is not None
        ]

        return {
            "total_trades": len(trades),
            "win_rate": round(
                len(wins) / len(trades) * 100,
                2
            ),
            "favorite_pair": (
                pairs.most_common(1)[0][0]
                if pairs else None
            ),
            "favorite_strategy": (
                strategies.most_common(1)[0][0]
                if strategies else None
            ),
            "average_profit": (
                round(sum(profits) / len(profits), 2)
                if profits else 0
            )
        }