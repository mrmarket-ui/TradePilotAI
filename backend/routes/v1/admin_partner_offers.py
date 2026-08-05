from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.admin import require_admin
from models.partner import Partner
from models.partner_review import PartnerOffer
from models.user import User
from schemas.partner_review import (
    OfferCreate,
    OfferUpdate,
)


router = APIRouter(
    prefix="/admin/partner-offers",
    tags=["Admin Partner Offers"],
)


@router.get("")
def list_offers(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    offers = (
        db.query(PartnerOffer)
        .order_by(
            PartnerOffer.created_at.desc()
        )
        .all()
    )

    return {
        "total": len(offers),
        "offers": offers,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_offer(
    payload: OfferCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    partner = db.query(Partner).filter(
        Partner.id == payload.partner_id
    ).first()

    if not partner:
        raise HTTPException(
            status_code=404,
            detail="Partner not found.",
        )

    offer = PartnerOffer(
        **payload.model_dump()
    )

    db.add(offer)
    db.commit()
    db.refresh(offer)

    return offer


@router.patch("/{offer_id}")
def update_offer(
    offer_id: int,
    payload: OfferUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    offer = db.query(PartnerOffer).filter(
        PartnerOffer.id == offer_id
    ).first()

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(offer, key, value)

    db.commit()
    db.refresh(offer)

    return offer


@router.delete("/{offer_id}")
def disable_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    offer = db.query(PartnerOffer).filter(
        PartnerOffer.id == offer_id
    ).first()

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    offer.active = False

    db.commit()

    return {
        "success": True,
        "active": False,
    }
