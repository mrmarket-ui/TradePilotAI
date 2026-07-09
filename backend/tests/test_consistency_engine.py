from datetime import datetime

from services.consistency.engine import (
    analyze_consistency,
)


class Trade:

    def __init__(
        self,
        pair,
        strategy,
        profit,
        hour,
        weekday,
        month,
    ):

        self.pair = pair
        self.strategy = strategy
        self.profit = profit

        self.opened_at = datetime(
            2026,
            month,
            weekday + 1,
            hour,
            0,
        )

        self.closed_at = datetime(
            2026,
            month,
            weekday + 1,
            hour + 1,
            0,
        )


trades = [

    Trade("XAUUSD","Liquidity",120,9,1,1),

    Trade("XAUUSD","Liquidity",-50,10,2,1),

    Trade("EURUSD","SMC",180,14,3,2),

    Trade("NAS100","Breakout",250,15,4,3),

]

statistics = {

    "win_rate":75,

    "profit_factor":2.1,

}

risk = {

    "recovery_factor":3.2,

}

psychology = {

    "score":88,

}

behavior = {

    "score":91,

}

report = analyze_consistency(

    trades,

    statistics,

    risk,

    psychology,

    behavior,

)

print(report.keys())

print(report["score"])

print(report["trend"])

print(report["symbols"])

print(report["strategies"])
