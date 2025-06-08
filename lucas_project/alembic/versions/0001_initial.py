"""Initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trend_seeds",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("phrase", sa.String, unique=True, nullable=False),
    )
    op.create_table(
        "domains",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain", sa.String, unique=True, nullable=False, index=True),
        sa.Column("trend_seed_id", sa.Integer, sa.ForeignKey("trend_seeds.id")),
        sa.Column("status", sa.String, nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "availability_checks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain_id", sa.Integer, sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("checked_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("available", sa.Boolean, nullable=False),
    )
    op.create_table(
        "valuations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain_id", sa.Integer, sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("service", sa.String, nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "monitors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain_id", sa.Integer, sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("service", sa.String, nullable=False),
        sa.Column("monitor_ref", sa.String, nullable=False),
    )
    op.create_table(
        "backorders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain_id", sa.Integer, sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("provider", sa.String, nullable=False),
        sa.Column("ordered_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "listings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain_id", sa.Integer, sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("marketplace", sa.String, nullable=False),
        sa.Column("url", sa.String),
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
    )


def downgrade() -> None:
    op.drop_table("listings")
    op.drop_table("backorders")
    op.drop_table("monitors")
    op.drop_table("valuations")
    op.drop_table("availability_checks")
    op.drop_table("domains")
    op.drop_table("trend_seeds")
