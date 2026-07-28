from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db

from services.paypal.client import (
    PayPalAPIError,
    PayPalConfigurationError,
)
from services.paypal.verifier import (
    verify_webhook_signature,
)
from services.paypal.webhook import (
    process_paypal_event,
)


router = APIRouter(
    prefix="/paypal",
    tags=["PayPal"],
)


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
)
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        event = await request.json()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON body.",
        ) from exc

    try:
        verified = (
            verify_webhook_signature(
                headers=request.headers,
                event=event,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except PayPalConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except PayPalAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "paypal_status_code":
                    exc.status_code,
                "paypal_details":
                    exc.details,
            },
        ) from exc

    if not verified:
        raise HTTPException(
            status_code=400,
            detail=(
                "PayPal webhook signature "
                "verification failed."
            ),
        )

    result = process_paypal_event(
        db=db,
        event=event,
    )

    return {
        "received": True,
        **result,
    }
