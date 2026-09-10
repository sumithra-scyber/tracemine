"""
Abstract interface for LLM-based classification of ambiguous emails.

Only emails the rule engine could NOT confidently classify reach this stage.
We send the minimum possible context - sender domain, subject, and Gmail's
own short snippet - never the full email body, and never the whole inbox.

To swap providers, implement LLMClassifier and update get_llm_classifier()
in providers/__init__.py. Nothing else in the codebase needs to change.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMClassificationResult:
    classification: str  # "ACCOUNT_EVIDENCE" | "NOT_ACCOUNT_EVIDENCE"
    confidence: int       # 0-100
    reason: str
    platform: str | None


class LLMClassifier(ABC):
    @abstractmethod
    def classify(self, sender_domain: str, subject: str, snippet: str) -> LLMClassificationResult:
        """Classify a single ambiguous email. Implementations must not log
        or persist the raw content beyond what's needed for this call."""
        raise NotImplementedError
