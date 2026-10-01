"""add mt5 autotrader settings

Revision ID: 5a8f1c9d3e42
Revises: 2c74a19e6f31
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5a8f1c9d3e42"
down_revision: Union[str, None] = "2c74a19e6f31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "broker_accounts",
        sa.Column(
            "autotrader_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "broker_accounts",
        sa.Column(
            "max_hold_minutes",
            sa.Integer(),
            nullable=False,
            server_default="30",
        ),
    )

    op.create_check_constraint(
        "ck_broker_accounts_max_hold_minutes",
        "broker_accounts",
        "max_hold_minutes IN (30, 60)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_broker_accounts_max_hold_minutes",
        "broker_accounts",
        type_="check",
    )

    op.drop_column(
        "broker_accounts",
        "max_hold_minutes",
    )

    op.drop_column(
        "broker_accounts",
        "autotrader_enabled",
    )
