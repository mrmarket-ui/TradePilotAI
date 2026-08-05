from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from database.database import Base


class PartnerReview(Base):
    __tablename__ = "partner_reviews"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "partner_id",
            name="uq_partner_review_user",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
    )

    partner_id = Column(
        Integer,
        ForeignKey(
            "partners.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    rating = Column(
        Integer,
        nullable=False,
    )

    review = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class PartnerOffer(Base):
    __tablename__ = "partner_offers"

    id = Column(
        Integer,
        primary_key=True,
    )

    partner_id = Column(
        Integer,
        ForeignKey(
            "partners.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    coupon_code = Column(
        String(100),
        nullable=True,
    )

    offer_url = Column(
        Text,
        nullable=True,
    )

    active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    expires_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
