"""add sign-in security tables (emailed codes, reset links, session version)

Safe to run more than once, and safe if the tables were already created by the
application on start-up: each table is only created when it is missing.

Revision ID: 9c1d5e7a2b40
Revises: 7b2e1d4f6a90
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9c1d5e7a2b40"
down_revision: Union[str, None] = "7b2e1d4f6a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _existing_tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    existing = _existing_tables()

    if "auth_challenges" not in existing:
        op.create_table(
            "auth_challenges",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("challenge_id", sa.String(length=64), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("purpose", sa.String(length=30), nullable=False),
            sa.Column("code_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False),
            sa.Column("resend_count", sa.Integer(), nullable=False),
            sa.Column("last_sent_at", sa.DateTime(), nullable=False),
            sa.Column("consumed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_auth_challenges_id"), "auth_challenges", ["id"], unique=False)
        op.create_index(op.f("ix_auth_challenges_challenge_id"), "auth_challenges", ["challenge_id"], unique=True)
        op.create_index(op.f("ix_auth_challenges_user_id"), "auth_challenges", ["user_id"], unique=False)

    if "password_reset_tokens" not in existing:
        op.create_table(
            "password_reset_tokens",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_password_reset_tokens_id"), "password_reset_tokens", ["id"], unique=False)
        op.create_index(op.f("ix_password_reset_tokens_user_id"), "password_reset_tokens", ["user_id"], unique=False)
        op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"], unique=True)

    if "auth_security" not in existing:
        op.create_table(
            "auth_security",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_version", sa.Integer(), nullable=False),
            sa.Column("password_changed_at", sa.DateTime(), nullable=True),
            sa.Column("last_login_at", sa.DateTime(), nullable=True),
            sa.Column("terms_accepted_at", sa.DateTime(), nullable=True),
            sa.Column("email_verified_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("user_id"),
        )


def downgrade() -> None:
    existing = _existing_tables()

    for table in ("auth_security", "password_reset_tokens", "auth_challenges"):
        if table in existing:
            op.drop_table(table)
