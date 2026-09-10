import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.account import ConfidenceLevel
from app.models.evidence import EvidenceType, ClassificationSource


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    platform_name: str
    primary_domain: str
    confidence_level: ConfidenceLevel
    confidence_score: int
    first_evidence_at: datetime
    last_evidence_at: datetime
    is_ghost: bool


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject: str
    sender_domain: str
    email_date: datetime
    evidence_type: EvidenceType
    confidence: int
    classification_source: ClassificationSource
    reason: str
