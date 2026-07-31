"""Add regions and competencies.

Revision ID: 20260731_0002
Revises: 20260730_0001
Create Date: 2026-07-31
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260731_0002"
down_revision: str | None = "20260730_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "regions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("macroregion", sa.String(length=32), nullable=False),
        sa.Column("market_priority", sa.SmallInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        sa.CheckConstraint(
            "market_priority BETWEEN 1 AND 2",
            name="ck_regions_market_priority",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_regions_code"), "regions", ["code"], unique=True)
    op.create_index(op.f("ix_regions_is_active"), "regions", ["is_active"], unique=False)
    op.create_index(op.f("ix_regions_macroregion"), "regions", ["macroregion"], unique=False)
    op.create_index(op.f("ix_regions_name"), "regions", ["name"], unique=True)

    op.create_table(
        "competencies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
    op.create_index(
        op.f("ix_competencies_category"),
        "competencies",
        ["category"],
        unique=False,
    )
    op.create_index(op.f("ix_competencies_code"), "competencies", ["code"], unique=True)
    op.create_index(
        op.f("ix_competencies_is_active"),
        "competencies",
        ["is_active"],
        unique=False,
    )
    op.create_index(op.f("ix_competencies_name"), "competencies", ["name"], unique=True)

    op.add_column("companies", sa.Column("region_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_companies_region_id_regions",
        "companies",
        "regions",
        ["region_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_companies_region_id"), "companies", ["region_id"], unique=False)

    op.create_table(
        "company_competencies",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("competency_id", sa.Uuid(), nullable=False),
        sa.Column("experience_level", sa.Integer(), nullable=False),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint(
            "experience_level BETWEEN 1 AND 5",
            name="ck_company_competencies_experience_level",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["competency_id"],
            ["competencies.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("company_id", "competency_id"),
    )


def downgrade() -> None:
    op.drop_table("company_competencies")
    op.drop_index(op.f("ix_companies_region_id"), table_name="companies")
    op.drop_constraint("fk_companies_region_id_regions", "companies", type_="foreignkey")
    op.drop_column("companies", "region_id")

    op.drop_index(op.f("ix_competencies_name"), table_name="competencies")
    op.drop_index(op.f("ix_competencies_is_active"), table_name="competencies")
    op.drop_index(op.f("ix_competencies_code"), table_name="competencies")
    op.drop_index(op.f("ix_competencies_category"), table_name="competencies")
    op.drop_table("competencies")

    op.drop_index(op.f("ix_regions_name"), table_name="regions")
    op.drop_index(op.f("ix_regions_macroregion"), table_name="regions")
    op.drop_index(op.f("ix_regions_is_active"), table_name="regions")
    op.drop_index(op.f("ix_regions_code"), table_name="regions")
    op.drop_table("regions")
