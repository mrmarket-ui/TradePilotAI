from datetime import datetime, timedelta
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.admin import require_admin
from models.partner import (
    Partner,
    PartnerClick,
    SavedPartner,
)
from models.user import User
from schemas.partner import (
    PartnerCreate,
    PartnerResponse,
    PartnerUpdate,
)


router = APIRouter(
    prefix="/admin/partners",
    tags=["Admin Partners"],
)


@router.get("")
def admin_list_partners(
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    partners = (
        db.query(Partner)
        .order_by(
            Partner.display_order.asc(),
            Partner.created_at.desc(),
        )
        .all()
    )

    return {
        "total": len(partners),
        "partners": partners,
    }


@router.post(
    "",
    response_model=PartnerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_partner(
    payload: PartnerCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    existing = (
        db.query(Partner)
        .filter(
            Partner.slug
            == payload.slug.strip().lower()
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Partner slug already exists.",
        )

    partner = Partner(
        **payload.model_dump()
    )

    partner.slug = (
        partner.slug.strip().lower()
    )

    partner.category = (
        partner.category.strip().lower()
    )

    db.add(partner)
    db.commit()
    db.refresh(partner)

    return partner


@router.patch(
    "/{partner_id}",
    response_model=PartnerResponse,
)
def update_partner(
    partner_id: int,
    payload: PartnerUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
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

    updates = payload.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(partner, key, value)

    if partner.slug:
        partner.slug = (
            partner.slug.strip().lower()
        )

    if partner.category:
        partner.category = (
            partner.category
            .strip()
            .lower()
        )

    db.commit()
    db.refresh(partner)

    return partner


@router.patch("/{partner_id}/status")
def update_partner_status(
    partner_id: int,
    partner_status: str = Query(
        alias="status"
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    valid = {
        "active",
        "paused",
        "coming_soon",
        "expired",
    }

    clean = partner_status.strip().lower()

    if clean not in valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid partner status.",
        )

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

    partner.status = clean

    db.commit()

    return {
        "id": partner.id,
        "status": partner.status,
    }


@router.get("/analytics/overview")
def partner_analytics(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    since = datetime.utcnow() - timedelta(days=days)

    total_clicks = (
        db.query(
            func.count(PartnerClick.id)
        )
        .filter(
            PartnerClick.clicked_at >= since
        )
        .scalar()
        or 0
    )

    total_partners = (
        db.query(
            func.count(Partner.id)
        )
        .scalar()
        or 0
    )

    active_partners = (
        db.query(
            func.count(Partner.id)
        )
        .filter(
            Partner.status == "active"
        )
        .scalar()
        or 0
    )

    saved_count = (
        db.query(
            func.count(SavedPartner.id)
        )
        .scalar()
        or 0
    )

    partner_rows = (
        db.query(
            Partner.id,
            Partner.name,
            Partner.category,
            func.count(
                PartnerClick.id
            ).label("clicks"),
        )
        .outerjoin(
            PartnerClick,
            (PartnerClick.partner_id == Partner.id)
            & (PartnerClick.clicked_at >= since),
        )
        .group_by(
            Partner.id,
            Partner.name,
            Partner.category,
        )
        .order_by(
            func.count(
                PartnerClick.id
            ).desc()
        )
        .all()
    )

    source_rows = (
        db.query(
            PartnerClick.source,
            func.count(
                PartnerClick.id
            ).label("clicks"),
        )
        .filter(
            PartnerClick.clicked_at >= since
        )
        .group_by(
            PartnerClick.source
        )
        .order_by(
            func.count(
                PartnerClick.id
            ).desc()
        )
        .all()
    )

    return {
        "days": days,
        "total_clicks": total_clicks,
        "total_partners": total_partners,
        "active_partners": active_partners,
        "saved_count": saved_count,
        "partners": [
            {
                "partner_id": row.id,
                "name": row.name,
                "category": row.category,
                "clicks": row.clicks,
            }
            for row in partner_rows
        ],
        "sources": [
            {
                "source": row.source,
                "clicks": row.clicks,
            }
            for row in source_rows
        ],
    }

