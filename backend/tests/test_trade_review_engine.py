from pprint import pprint

from services.trade_review.engine import review_trade


class Trade:
    profit = -25
    entry = 100
    stop_loss = 99
    take_profit = 100.5
    strategy = "Unspecified"
    lot_size = 0.10
    opened_at = None
    closed_at = None


pprint(
    review_trade(
        Trade()
    )
)
