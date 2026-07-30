"""Create companies table.

Revision ID: 20260730_0001
Revises:
Create Date: 2026-07-30
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260730_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("edrpou", sa.String(length=8), nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_city"), "companies", ["city"], unique=False)
    op.create_index(op.f("ix_companies_edrpou"), "companies", ["edrpou"], unique=True)
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=False)
    op.create_index(op.f("ix_companies_region"), "companies", ["region"], unique=False)
    op.create_index(op.f("ix_companies_status"), "companies", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_companies_status"), table_name="companies")
    op.drop_index(op.f("ix_companies_region"), table_name="companies")
    op.drop_index(op.f("ix_companies_name"), table_name="companies")
    op.drop_index(op.f("ix_companies_edrpou"), table_name="companies")
    op.drop_index(op.f("ix_companies_city"), table_name="companies")
    op.drop_table("companies")
