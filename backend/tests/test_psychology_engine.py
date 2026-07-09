from datetime import datetime

from services.psychology.engine import (
    analyze_psychology,
)


class Trade:

    def __init__(self, profit):

        self.profit = profit

        self.opened_at = datetime.now()

        self.closed_at = datetime.now()


trades = [

    Trade(100),

    Trade(200),

    Trade(-50),

    Trade(150),

]

behavior = {

    "revenge_trading": True,

    "fomo_detected": False,

    "holding_losers_too_long": True,

    "cutting_winners_too_early": False,

    "position_size_discipline": True,

    "strategy_discipline": True,

    "session_discipline": True,

    "weekend_trading": False,

}

print(

    analyze_psychology(

        trades,

        behavior,

        consistency_trend="improving",

    )

)