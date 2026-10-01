from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import require_premium_plan

from models.user import User
from models.broker_account import BrokerAccount

from services.trades.sync import sync_account

router = APIRouter(
    prefix="/trading",
    tags=["Trading"]
)


@router.post("/sync")
def sync_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan
    )
):
    accounts = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.user_id == current_user.id,
            BrokerAccount.connected.is_(True),
        )
        .all()
    )

    if not accounts:
        raise HTTPException(
            status_code=404,
            detail="No MT5 accounts connected."
        )

    imported = 0
    skipped = 0
    synced_accounts = 0
    failed_accounts = []

    for account in accounts:
        result = sync_account(
            db,
            account
        )

        if not result["success"]:
            failed_accounts.append(
                {
                    "account_id": account.id,
                    "message": result.get(
                        "message",
                        "MT5 sync failed.",
                    ),
                }
            )
            continue

        synced_accounts += 1
        imported += result["imported"]
        skipped += result["skipped"]

    return {
        "accounts": len(accounts),
        "synced_accounts": synced_accounts,
        "failed_accounts": failed_accounts,
        "imported": imported,
        "skipped": skipped,
        "status": (
            "success"
            if not failed_accounts
            else "partial"
        ),
    }
