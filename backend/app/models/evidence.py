import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class EvidenceType(str, enum.Enum):
    PASSWORD_RESET = "password_reset"
    ACCOUNT_VERIFICATION = "account_verification"
    WELCOME_EMAIL = "welcome_email"
    SECURITY_NOTICE = "security_notice"
    PURCHASE_RECEIPT = "purchase_receipt"
    NEWSLETTER = "newsletter"
    OTHER = "other"


class ClassificationSource(str, enum.Enum):
    RULE = "rule"
    LLM = "llm"


class EmailEvidence(Base):
    """
    A single piece of evidence extracted from one email.

    DATA MINIMIZATION:
    We deliberately do NOT store the full email body. We keep only what's
    needed to justify a classification to the user later:
      - sender domain/address (to identify the platform)
      - subject line (short, usually enough context on its own)
      - a short reason string (from the rule engine or LLM)
    The Gmail message id is kept so we could re-fetch fresh detail on demand,
    but we never persist the raw message content itself.
    """

    __tablename__ = "email_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )

    gmail_message_id: Mapped[str] = mapped_column(String, nullable=False)
    sender_domain: Mapped[str] = mapped_column(String, nullable=False, index=True)
    sender_address: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    email_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    evidence_type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType), nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    classification_source: Mapped[ClassificationSource] = mapped_column(
        Enum(ClassificationSource), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
