import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.scan_job import ScanStatus


class ScanJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ScanStatus
    candidate_emails_found: int
    emails_classified: int
    accounts_discovered: int
    error_message: str | None
