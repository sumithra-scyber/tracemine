import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    SEARCHING = "searching"
    CLASSIFYING = "classifying"
    BUILDING_INVENTORY = "building_inventory"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanJob(Base):
    """
    Tracks the progress of a single scan run so the frontend can poll for
    real status instead of guessing with a client-side timer.

    Counts are updated incrementally by scan_service as it works through
    Gmail search results, so /scan/status can report meaningful, real
    numbers (not simulated ones).
    """

    __tablename__ = "scan_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus), nullable=False, default=ScanStatus.PENDING
    )

    candidate_emails_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    emails_classified: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accounts_discovered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
