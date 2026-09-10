"""add scan_jobs table

Revision ID: 0002_scan_jobs
Revises: 0001_initial
Create Date: 2026-09-06
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_scan_jobs"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "searching", "classifying", "building_inventory",
                "completed", "failed",
                name="scanstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("candidate_emails_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("emails_classified", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accounts_discovered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_scan_jobs_user_id", "scan_jobs", ["user_id"])


def downgrade() -> None:
    op.drop_table("scan_jobs")
    op.execute("DROP TYPE IF EXISTS scanstatus")
