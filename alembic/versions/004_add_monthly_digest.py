"""Add monthly digest columns

Revision ID: 004_add_monthly_digest
Revises: 003_add_alert_settings
Create Date: 2024-01-15
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_add_monthly_digest"
down_revision: Union[str, None] = "003_add_alert_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("alert_settings", sa.Column("digest_monthly", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column("alert_settings", sa.Column("last_monthly_digest", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("alert_settings", "last_monthly_digest")
    op.drop_column("alert_settings", "digest_monthly")
