from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.partner import Partner
from models.partner_review import PartnerOffer, PartnerReview
from models.user import User
from schemas.partner_review import ReviewCreate


router = APIRouter(
    prefix="/partners",
    tags=["Partner Reviews & Offers"],
)


@router.get("/{partner_id}/reviews")
def get_reviews(
    partner_id: int,
    db: Session = Depends(get_db),
):
    partner = db.query(Partner).filter(
        Partner.id == partner_id
    ).first()

    if not partner:
        raise HTTPException(
            status_code=404,
            detail="Partner not found.",
        )

    reviews = (
        db.query(PartnerReview, User)
        .join(
            User,
            User.id == PartnerReview.user_id,
        )
        .filter(
            PartnerReview.partner_id == partner_id
        )
        .order_by(
            PartnerReview.created_at.desc()
        )
        .all()
    )

    average = (
        db.query(
            func.avg(PartnerReview.rating)
        )
        .filter(
            PartnerReview.partner_id == partner_id
        )
        .scalar()
    )

    return {
        "average_rating": (
            round(float(average), 1)
            if average
            else 0
        ),
        "review_count": len(reviews),
        "reviews": [
            {
                "id": review.id,
                "rating": review.rating,
                "review": review.review,
                "created_at": review.created_at,
                "user": (
                    user.username
                    or user.full_name
                    or "TradePilot User"
                ),
            }
            for review, user in reviews
        ],
    }


@router.post("/{partner_id}/reviews")
def create_or_update_review(
    partner_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    partner = db.query(Partner).filter(
        Partner.id == partner_id,
        Partner.status == "active",
    ).first()

    if not partner:
        raise HTTPException(
            status_code=404,
            detail="Partner not found.",
        )

    review = db.query(PartnerReview).filter(
        PartnerReview.partner_id == partner_id,
        PartnerReview.user_id == current_user.id,
    ).first()

    if review:
        review.rating = payload.rating
        review.review = payload.review
        review.updated_at = datetime.utcnow()

    else:
        review = PartnerReview(
            partner_id=partner_id,
            user_id=current_user.id,
            rating=payload.rating,
            review=payload.review,
        )

        db.add(review)

    db.commit()
    db.refresh(review)

    return {
        "success": True,
        "review_id": review.id,
        "rating": review.rating,
    }


@router.get("/{partner_id}/offers")
def get_partner_offers(
    partner_id: int,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()

    offers = (
        db.query(PartnerOffer)
        .filter(
            PartnerOffer.partner_id == partner_id,
            PartnerOffer.active.is_(True),
        )
        .order_by(
            PartnerOffer.created_at.desc()
        )
        .all()
    )

    valid = [
        offer
        for offer in offers
        if (
            offer.expires_at is None
            or offer.expires_at > now
        )
    ]

    return [
        {
            "id": offer.id,
            "partner_id": offer.partner_id,
            "title": offer.title,
            "description": offer.description,
            "coupon_code": offer.coupon_code,
            "offer_url": offer.offer_url,
            "expires_at": offer.expires_at,
        }
        for offer in valid
    ]
