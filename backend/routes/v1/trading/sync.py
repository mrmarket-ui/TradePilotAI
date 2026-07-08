from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user

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
    current_user: User = Depends(get_current_user)
):

    accounts = db.query(
        BrokerAccount
    ).filter(
        BrokerAccount.user_id == current_user.id
    ).all()

    if not accounts:

        raise HTTPException(
            status_code=404,
            detail="No broker accounts connected."
        )

    imported = 0
    skipped = 0

    for account in accounts:

        result = sync_account(
            db,
            account
        )

        if not result["success"]:
            continue

        imported += result["imported"]
        skipped += result["skipped"]

    return {
        "accounts": len(accounts),
        "imported": imported,
        "skipped": skipped,
        "status": "success"
    }