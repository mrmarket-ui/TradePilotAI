from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)

from database.database import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(160),
        nullable=False,
    )

    slug = Column(
        String(180),
        nullable=False,
        unique=True,
        index=True,
    )

    category = Column(
        String(30),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    referral_url = Column(
        Text,
        nullable=False,
    )

    badge = Column(
        String(100),
        nullable=True,
    )

    logo_url = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="active",
        index=True,
    )

    featured = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    display_order = Column(
        Integer,
        nullable=False,
        default=0,
    )

    minimum_deposit = Column(
        String(100),
        nullable=True,
    )

    platforms = Column(
        JSON,
        nullable=True,
    )

    demo_available = Column(
        Boolean,
        nullable=True,
    )

    regulation = Column(
        String(255),
        nullable=True,
    )

    challenge_size = Column(
        String(100),
        nullable=True,
    )

    challenge_fee = Column(
        String(100),
        nullable=True,
    )

    profit_split = Column(
        String(100),
        nullable=True,
    )

    max_drawdown = Column(
        String(100),
        nullable=True,
    )

    payout_frequency = Column(
        String(100),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class PartnerClick(Base):
    __tablename__ = "partner_clicks"

    id = Column(Integer, primary_key=True, index=True)

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
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    source = Column(
        String(80),
        nullable=False,
        default="partners_page",
        index=True,
    )

    clicked_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )


class SavedPartner(Base):
    __tablename__ = "saved_partners"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "partner_id",
            name="uq_saved_partner_user",
        ),
    )

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
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

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
