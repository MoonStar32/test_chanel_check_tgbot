"""Add alert settings table

Revision ID: 003_add_alert_settings
Revises: 002_add_users
Create Date: 2024-01-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_alert_settings"
down_revision: Union[str, None] = "002_add_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alert_settings",
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("mass_leave_threshold", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("mass_leave_window_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("anomaly_factor", sa.Float(), nullable=False, server_default="3.0"),
        sa.Column("milestone_step", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("last_milestone", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("digest_daily", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("digest_weekly", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("quiet_hours_start", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quiet_hours_end", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("churn_percent_threshold", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("vip_user_ids", sa.Text(), nullable=True),
        sa.Column("last_churn_alert_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_daily_digest", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_weekly_digest", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("channel_id"),
    )


def downgrade() -> None:
    op.drop_table("alert_settings")
