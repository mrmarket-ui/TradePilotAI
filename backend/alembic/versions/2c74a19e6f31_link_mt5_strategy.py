"""link mt5 broker accounts to strategy profiles

Revision ID: 2c74a19e6f31
Revises: 8fbe88df22db
Create Date: 2026-09-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2c74a19e6f31"
down_revision: Union[str, Sequence[str], None] = "8fbe88df22db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "broker_accounts",
        sa.Column(
            "strategy_profile_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_broker_accounts_strategy_profile_id",
        "broker_accounts",
        ["strategy_profile_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_broker_accounts_strategy_profile_id",
        "broker_accounts",
        "strategy_profiles",
        ["strategy_profile_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_broker_accounts_strategy_profile_id",
        "broker_accounts",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_broker_accounts_strategy_profile_id",
        table_name="broker_accounts",
    )

    op.drop_column(
        "broker_accounts",
        "strategy_profile_id",
    )
