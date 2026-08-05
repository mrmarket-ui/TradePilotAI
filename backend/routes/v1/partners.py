from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.partner import (
    Partner,
    PartnerClick,
    SavedPartner,
)
from models.user import User
from schemas.partner import (
    PartnerClickRequest,
    PartnerResponse,
)


router = APIRouter(
    prefix="/partners",
    tags=["Partners"],
)


@router.get(
    "",
    response_model=list[PartnerResponse],
)
def list_partners(
    category: str | None = None,
    search: str | None = None,
    featured: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Partner).filter(
        Partner.status == "active"
    )

    if category:
        query = query.filter(
            Partner.category
            == category.strip().lower()
        )

    if featured is not None:
        query = query.filter(
            Partner.featured == featured
        )

    if search:
        pattern = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Partner.name.ilike(pattern),
                Partner.description.ilike(pattern),
                Partner.badge.ilike(pattern),
            )
        )

    return (
        query
        .order_by(
            Partner.featured.desc(),
            Partner.display_order.asc(),
            Partner.name.asc(),
        )
        .all()
    )


@router.get(
    "/saved",
    response_model=list[PartnerResponse],
)
def saved_partners(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    return (
        db.query(Partner)
        .join(
            SavedPartner,
            SavedPartner.partner_id
            == Partner.id,
        )
        .filter(
            SavedPartner.user_id
            == current_user.id
        )
        .order_by(
            SavedPartner.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{slug}",
    response_model=PartnerResponse,
)
def partner_detail(
    slug: str,
    db: Session = Depends(get_db),
):
    partner = (
        db.query(Partner)
        .filter(
            Partner.slug == slug,
            Partner.status == "active",
        )
        .first()
    )

    if partner is None:
        raise HTTPException(
            status_code=404,
            detail="Partner not found.",
        )

    return partner


@router.post("/{partner_id}/click")
def track_partner_click(
    partner_id: int,
    payload: PartnerClickRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    partner = (
        db.query(Partner)
        .filter(
            Partner.id == partner_id,
            Partner.status == "active",
        )
        .first()
    )

    if partner is None:
        raise HTTPException(
            status_code=404,
            detail="Partner not found.",
        )

    click = PartnerClick(
        partner_id=partner.id,
        user_id=current_user.id,
        source=payload.source,
    )

    db.add(click)
    db.commit()

    return {
        "success": True,
        "partner_id": partner.id,
        "redirect_url": partner.referral_url,
    }


@router.post("/{partner_id}/save")
def save_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    partner = (
        db.query(Partner)
        .filter(
            Partner.id == partner_id
        )
        .first()
    )

    if partner is None:
        raise HTTPException(
            status_code=404,
            detail="Partner not found.",
        )

    existing = (
        db.query(SavedPartner)
        .filter(
            SavedPartner.user_id
            == current_user.id,
            SavedPartner.partner_id
            == partner_id,
        )
        .first()
    )

    if existing:
        return {
            "saved": True,
            "message": (
                "Partner already saved."
            ),
        }

    saved = SavedPartner(
        user_id=current_user.id,
        partner_id=partner_id,
    )

    db.add(saved)
    db.commit()

    return {
        "saved": True,
        "partner_id": partner_id,
    }


@router.delete("/{partner_id}/save")
def unsave_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    saved = (
        db.query(SavedPartner)
        .filter(
            SavedPartner.user_id
            == current_user.id,
            SavedPartner.partner_id
            == partner_id,
        )
        .first()
    )

    if saved is None:
        return {
            "saved": False,
        }

    db.delete(saved)
    db.commit()

    return {
        "saved": False,
        "partner_id": partner_id,
    }
