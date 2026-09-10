"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-06
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_scan_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "oauth_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("encrypted_access_token", sa.LargeBinary(), nullable=False),
        sa.Column("encrypted_refresh_token", sa.LargeBinary(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform_name", sa.String(), nullable=False),
        sa.Column("primary_domain", sa.String(), nullable=False),
        sa.Column(
            "confidence_level",
            sa.Enum("strong", "weak", "uncertain", name="confidencelevel"),
            nullable=False,
        ),
        sa.Column("confidence_score", sa.Integer(), nullable=False),
        sa.Column("first_evidence_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_evidence_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_ghost", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])
    op.create_index("ix_accounts_primary_domain", "accounts", ["primary_domain"])

    op.create_table(
        "email_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("gmail_message_id", sa.String(), nullable=False),
        sa.Column("sender_domain", sa.String(), nullable=False),
        sa.Column("sender_address", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("email_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "evidence_type",
            sa.Enum(
                "password_reset", "account_verification", "welcome_email",
                "security_notice", "purchase_receipt", "newsletter", "other",
                name="evidencetype",
            ),
            nullable=False,
        ),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column(
            "classification_source",
            sa.Enum("rule", "llm", name="classificationsource"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_email_evidence_user_id", "email_evidence", ["user_id"])
    op.create_index("ix_email_evidence_account_id", "email_evidence", ["account_id"])
    op.create_index("ix_email_evidence_sender_domain", "email_evidence", ["sender_domain"])


def downgrade() -> None:
    op.drop_table("email_evidence")
    op.drop_table("accounts")
    op.drop_table("oauth_tokens")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS confidencelevel")
    op.execute("DROP TYPE IF EXISTS evidencetype")
    op.execute("DROP TYPE IF EXISTS classificationsource")
