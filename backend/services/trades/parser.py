from datetime import datetime

from models.trade import Trade


def parse_deal(
    deal,
    user_id: int,
    broker: str
):

    direction = "BUY"

    if deal.type == 1:
        direction = "SELL"

    trade = Trade(
        user_id=user_id,
        broker=broker,

        ticket=str(deal.ticket),

        pair=deal.symbol,
        direction=direction,

        entry=deal.price,
        exit_price=deal.price,

        stop_loss=0,
        take_profit=0,

        lot_size=deal.volume,

        profit=deal.profit,
        commission=deal.commission,
        swap=deal.swap,

        magic_number=deal.magic,
        comment=deal.comment,

        opened_at=datetime.fromtimestamp(deal.time),
        closed_at=datetime.fromtimestamp(deal.time),

        imported=True
    )

    return trade