from datetime import datetime, timedelta

from services.behavior.engine import analyze_behavior


class Trade:

    def __init__(
        self,
        profit,
        opened,
        closed,
        strategy="SMC",
        lot_size=0.10,
    ):
        self.profit = profit
        self.opened_at = opened
        self.closed_at = closed
        self.strategy = strategy
        self.lot_size = lot_size

        self.entry = 100
        self.stop_loss = 99
        self.take_profit = 103


trades = [

    Trade(
        -100,
        datetime(2026, 7, 1, 9),
        datetime(2026, 7, 1, 10),
    ),

    Trade(
        150,
        datetime(2026, 7, 1, 10, 10),
        datetime(2026, 7, 1, 11),
    ),

    Trade(
        200,
        datetime(2026, 7, 2, 9),
        datetime(2026, 7, 2, 12),
    ),
]

print(analyze_behavior(trades))