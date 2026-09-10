"""
Ghost account scoring.

A Ghost Account is evidence of a past account with no recent signal. This is
a HEURISTIC, not a fact - we can never confirm an account still exists (or
was ever deleted) purely from email history. Every ghost determination must
stay explainable: which evidence exists, and how long it's been since the
last signal.
"""

from datetime import datetime, timezone

from app.config import get_settings
from app.models.account import Account


def is_ghost_account(account: Account, now: datetime | None = None) -> bool:
    settings = get_settings()
    now = now or datetime.now(timezone.utc)
    inactivity = now - account.last_evidence_at
    return inactivity.days >= settings.ghost_inactivity_days


def days_since_last_evidence(account: Account, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    return (now - account.last_evidence_at).days
