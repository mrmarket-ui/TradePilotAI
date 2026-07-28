from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User

from schemas.subscription import (
    PayPalSubscriptionCreateRequest,
    PayPalSubscriptionCreateResponse,
    PlanCatalogueResponse,
    PublicPlanResponse,
    SubscriptionResponse,
)

from services.paypal.client import (
    PayPalAPIError,
    PayPalConfigurationError,
)

from services.subscriptions.crud import (
    get_or_create_subscription,
    save_pending_paypal_subscription,
)

from services.subscriptions.paypal import (
    create_paypal_subscription,
)

from services.subscriptions.plans import (
    get_subscription_plan,
    get_subscription_plans,
)


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.get(
    "/plans",
    response_model=PlanCatalogueResponse,
)
def read_subscription_plans():
    plans = get_subscription_plans()

    return {
        "plans": [
            PublicPlanResponse(
                code=plan.code,
                name=plan.name,
                amount=plan.amount,
                currency=plan.currency,
                paypal_plan_id=(
                    plan.paypal_plan_id
                ),
            )
            for plan in plans.values()
        ]
    }


@router.get(
    "/me",
    response_model=SubscriptionResponse,
)
def read_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    return get_or_create_subscription(
        db=db,
        user_id=current_user.id,
    )


@router.post(
    "/paypal/create",
    response_model=(
        PayPalSubscriptionCreateResponse
    ),
    status_code=status.HTTP_201_CREATED,
)
def begin_paypal_subscription(
    payload: PayPalSubscriptionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    existing = get_or_create_subscription(
        db=db,
        user_id=current_user.id,
    )

    if existing.status == "active":
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "You already have an active "
                f"{existing.plan} subscription."
            ),
        )

    if (
        existing.status
        == "approval_pending"
        and existing.paypal_subscription_id
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "A PayPal subscription is "
                "already awaiting approval. "
                "Complete that checkout before "
                "creating another."
            ),
        )

    try:
        plan = get_subscription_plan(
            payload.plan,
        )

        paypal_result = (
            create_paypal_subscription(
                user_id=current_user.id,
                user_email=current_user.email,
                plan=plan,
            )
        )

        save_pending_paypal_subscription(
            db=db,
            user=current_user,
            plan=plan,
            paypal_subscription_id=(
                paypal_result[
                    "subscription_id"
                ]
            ),
            paypal_status=(
                paypal_result["status"]
            ),
        )

        return {
            **paypal_result,
            "plan": plan.code,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc

    except PayPalConfigurationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc

    except PayPalAPIError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail={
                "message": str(exc),
                "paypal_status_code": (
                    exc.status_code
                ),
                "paypal_details": (
                    exc.details
                ),
            },
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=str(exc),
        ) from exc
