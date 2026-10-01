"""add mt5 trade proposals

Revision ID: 7b2e1d4f6a90
Revises: 5a8f1c9d3e42
Create Date: 2026-09-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b2e1d4f6a90"
down_revision: Union[str, None] = "5a8f1c9d3e42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mt5_trade_proposals",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "broker_account_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "strategy_profile_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "symbol",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "direction",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "entry_price",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "stop_loss",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "take_profit",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "risk_percent",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "risk_reward",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "max_hold_minutes",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "timeframe_context",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "matched_rules",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "missing_rules",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "strategy_snapshot",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "analysis_summary",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "approved_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "rejected_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "executed_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),

        sa.ForeignKeyConstraint(
            ["broker_account_id"],
            ["broker_accounts.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["strategy_profile_id"],
            ["strategy_profiles.id"],
            ondelete="SET NULL",
        ),

        sa.CheckConstraint(
            "max_hold_minutes IN (30, 60)",
            name="ck_mt5_trade_proposals_max_hold_minutes",
        ),

        sa.CheckConstraint(
            "status IN "
            "('pending', 'approved', 'rejected', "
            "'expired', 'executed', 'failed')",
            name="ck_mt5_trade_proposals_status",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_mt5_trade_proposals_id",
        "mt5_trade_proposals",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_mt5_trade_proposals_user_id",
        "mt5_trade_proposals",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_mt5_trade_proposals_broker_account_id",
        "mt5_trade_proposals",
        ["broker_account_id"],
        unique=False,
    )

    op.create_index(
        "ix_mt5_trade_proposals_strategy_profile_id",
        "mt5_trade_proposals",
        ["strategy_profile_id"],
        unique=False,
    )

    op.create_index(
        "ix_mt5_trade_proposals_symbol",
        "mt5_trade_proposals",
        ["symbol"],
        unique=False,
    )

    op.create_index(
        "ix_mt5_trade_proposals_status",
        "mt5_trade_proposals",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mt5_trade_proposals_status",
        table_name="mt5_trade_proposals",
    )

    op.drop_index(
        "ix_mt5_trade_proposals_symbol",
        table_name="mt5_trade_proposals",
    )

    op.drop_index(
        "ix_mt5_trade_proposals_strategy_profile_id",
        table_name="mt5_trade_proposals",
    )

    op.drop_index(
        "ix_mt5_trade_proposals_broker_account_id",
        table_name="mt5_trade_proposals",
    )

    op.drop_index(
        "ix_mt5_trade_proposals_user_id",
        table_name="mt5_trade_proposals",
    )

    op.drop_index(
        "ix_mt5_trade_proposals_id",
        table_name="mt5_trade_proposals",
    )

    op.drop_table("mt5_trade_proposals")
