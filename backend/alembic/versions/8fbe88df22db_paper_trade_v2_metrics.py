"""paper trade v2 metrics

Revision ID: 8fbe88df22db
Revises: 785d82e048d3
Create Date: 2026-08-24 00:55:49.982350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fbe88df22db'
down_revision: Union[str, Sequence[str], None] = '785d82e048d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "paper_trades",
        sa.Column(
            "result",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "paper_trades",
        sa.Column(
            "r_multiple",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "paper_trades",
        sa.Column(
            "duration_minutes",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "paper_trades",
        "duration_minutes",
    )

    op.drop_column(
        "paper_trades",
        "r_multiple",
    )

    op.drop_column(
        "paper_trades",
        "result",
    )
