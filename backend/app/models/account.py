import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ConfidenceLevel(str, enum.Enum):
    STRONG = "strong"
    WEAK = "weak"
    UNCERTAIN = "uncertain"


class Account(Base):
    """
    A discovered account: one row per (user, platform).

    This is a derived/aggregate record built from one or more EmailEvidence
    rows. It is intentionally re-computable from evidence at any time - if a
    user deletes evidence, we recompute rather than trusting stale fields.
    """

    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    platform_name: Mapped[str] = mapped_column(String, nullable=False)
    primary_domain: Mapped[str] = mapped_column(String, nullable=False, index=True)

    confidence_level: Mapped[ConfidenceLevel] = mapped_column(Enum(ConfidenceLevel), nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100, max of its evidence

    first_evidence_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_evidence_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    is_ghost: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
