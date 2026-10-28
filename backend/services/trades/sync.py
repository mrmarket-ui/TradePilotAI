from datetime import datetime

from sqlalchemy.orm import Session

from models.broker_account import BrokerAccount
from models.trade import Trade

from services.security.encryption import decrypt
from services.brokers.mt5 import (
    connect,
    disconnect,
    get_history,
)

from services.trades.positions import build_trade_rows
from services.trades.saver import save_trade


def _namespaced_ticket(
    account: BrokerAccount,
    position_ticket: str,
) -> str:
    # MT5 position numbers are only unique per broker server, but
    # Trade.ticket is UNIQUE across the whole database. Without a prefix,
    # one user's trade could make another user's trade look like a
    # duplicate and be silently skipped.
    return (
        f"mt5:{account.server}:{account.account_number}:"
        f"{position_ticket}"
    )


def sync_account(
    db: Session,
    account: BrokerAccount,
):
    password = decrypt(
        account.encrypted_password
    )

    success, message = connect(
        int(account.account_number),
        password,
        account.server,
    )

    if not success:
        return {
            "success": False,
            "message": str(message),
        }

    try:
        deals = get_history(
            datetime(2000, 1, 1),
            datetime.now(),
        )

        rows, summary = build_trade_rows(
            deals
        )

        imported = 0
        skipped = 0

        for row in rows:
            row = dict(row)

            row["ticket"] = _namespaced_ticket(
                account,
                row["ticket"],
            )

            trade = Trade(
                user_id=account.user_id,
                broker=account.broker,
                **row,
            )

            saved = save_trade(
                db,
                trade,
            )

            if saved:
                imported += 1
            else:
                skipped += 1

        account.last_sync = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "positions": summary["positions"],
            "ignored_non_trade_deals": summary[
                "skipped_non_trade_deals"
            ],
            "open_positions": summary["open_positions"],
        }

    except Exception:
        db.rollback()
        raise

    finally:
        disconnect()