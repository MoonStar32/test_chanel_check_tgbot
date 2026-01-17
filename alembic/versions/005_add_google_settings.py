"""Add per-user Google Sheets settings

Revision ID: 005_add_google_settings
Revises: 004_add_monthly_digest
Create Date: 2024-01-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_add_google_settings"
down_revision: Union[str, None] = "004_add_monthly_digest"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "google_settings",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("creds_json", sa.Text(), nullable=True),
        sa.Column("spreadsheet_id", sa.String(length=255), nullable=True),
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
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("google_settings")
