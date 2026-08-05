import main

from database.database import SessionLocal
from models.partner import Partner


PARTNERS = [
    {
        "name": "VPropTrader",
        "slug": "vproptrader",
        "category": "prop_firm",
        "description": (
            "Register for a free $1,000 account "
            "challenge, test your trading skills "
            "and qualify for profit sharing if successful."
        ),
        "referral_url": (
            "https://vproptrader.com/share/"
            "yvc3h?invite=nkd8i16c"
        ),
        "badge": "Free $1,000 Challenge",
        "featured": True,
        "display_order": 1,
    },
    {
        "name": "FundedElite",
        "slug": "fundedelite",
        "category": "prop_firm",
        "description": (
            "Explore FundedElite proprietary "
            "trading challenges and funding opportunities."
        ),
        "referral_url": (
            "https://app.fundedelite.com"
            "?aff=AFF8683831"
        ),
        "badge": "Prop Firm",
        "display_order": 2,
    },
    {
        "name": "The5ers",
        "slug": "the5ers",
        "category": "prop_firm",
        "description": (
            "Explore proprietary trading programs "
            "and funding opportunities from The5ers."
        ),
        "referral_url": (
            "https://www.the5ers.com/?afmc=1dtk"
        ),
        "badge": "Prop Firm",
        "display_order": 3,
    },
    {
        "name": "DB Investing",
        "slug": "db-investing",
        "category": "broker",
        "description": (
            "Recommended broker available through "
            "the TradePilot AI partner network."
        ),
        "referral_url": (
            "https://my.dbinvesting.com/links/go/3766"
        ),
        "badge": "Recommended Broker",
        "featured": True,
        "display_order": 4,
    },
    {
        "name": "Headway",
        "slug": "headway",
        "category": "broker",
        "description": (
            "Broker option for traders looking for "
            "an accessible and cost-conscious trading platform."
        ),
        "referral_url": (
            "https://headway.partners/user/signup"
            "?hwp=12eab6"
        ),
        "badge": "Affordable Option",
        "display_order": 5,
    },
    {
        "name": "XM ZA",
        "slug": "xm-za",
        "category": "broker",
        "description": (
            "Explore XM through the TradePilot AI "
            "referral partnership."
        ),
        "referral_url": (
            "https://www.xmza.com/referral"
            "?token=ir4kDrpVX16S63SmNzNj3A"
        ),
        "badge": "Broker",
        "display_order": 6,
    },
]


db = SessionLocal()

try:
    for data in PARTNERS:
        existing = (
            db.query(Partner)
            .filter(
                Partner.slug
                == data["slug"]
            )
            .first()
        )

        if existing:
            print(
                "EXISTS:",
                existing.name,
            )
            continue

        partner = Partner(
            **data
        )

        db.add(partner)

        print(
            "ADDED:",
            data["name"],
        )

    db.commit()

finally:
    db.close()


print("Partner seed complete.")
