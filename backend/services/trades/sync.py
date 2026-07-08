from datetime import datetime

from sqlalchemy.orm import Session

from models.broker_account import BrokerAccount

from services.security.encryption import decrypt
from services.brokers.mt5 import (
    connect,
    disconnect,
    get_history
)

from services.trades.parser import parse_deal
from services.trades.saver import save_trade


def sync_account(
    db: Session,
    account: BrokerAccount
):

    password = decrypt(
        account.encrypted_password
    )

    success, message = connect(
        int(account.account_number),
        password,
        account.server
    )

    if not success:

        return {
            "success": False,
            "message": str(message)
        }

    deals = get_history(
        datetime(2000, 1, 1),
        datetime.now()
    )

    imported = 0
    skipped = 0

    for deal in deals:

        trade = parse_deal(
            deal,
            account.user_id,
            account.broker
        )

        saved = save_trade(
            db,
            trade
        )

        if saved:
            imported += 1
        else:
            skipped += 1

    account.last_sync = datetime.utcnow()

    db.commit()

    disconnect()

    return {
        "success": True,
        "imported": imported,
        "skipped": skipped
    }