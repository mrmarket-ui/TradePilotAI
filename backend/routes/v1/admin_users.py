from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.admin import require_admin
from models.user import User


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"],
)


@router.get("")
def list_admin_users(
    search: str | None = Query(
        default=None,
        max_length=120,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    query = db.query(User)

    if search:
        pattern = f"%{search.strip()}%"

        query = query.filter(
            (User.email.ilike(pattern))
            | (User.full_name.ilike(pattern))
            | (User.username.ilike(pattern))
        )

    total = query.count()

    users = (
        query
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "username": user.username,
                "plan": user.plan,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "ai_credits": user.ai_credits,
                "created_at": user.created_at,
            }
            for user in users
        ],
    }


@router.patch("/{user_id}/plan")
def change_user_plan(
    user_id: int,
    plan: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    normalized_plan = plan.strip().lower()

    if normalized_plan not in {
        "free",
        "pro",
        "premium",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PLAN",
                "message": (
                    "Plan must be free, pro or premium."
                ),
            },
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user.plan = normalized_plan

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "plan": user.plan,
    }


@router.patch("/{user_id}/status")
def change_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    if user_id == admin_user.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SELF_SUSPEND_BLOCKED",
                "message": (
                    "You cannot suspend your own admin account."
                ),
            },
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
    }


@router.patch("/{user_id}/ai-credits")
def change_ai_credits(
    user_id: int,
    credits: int = Query(
        ge=0,
        le=100000,
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user.ai_credits = credits

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "ai_credits": user.ai_credits,
    }
