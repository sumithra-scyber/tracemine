"""
Rule-based classification of candidate emails.

This is the first pass in the pipeline: Gmail search -> HERE -> LLM (only
for what's left ambiguous) -> account inventory. Rules handle the clear-cut
cases cheaply and without any external API call. Anything that doesn't
confidently match a rule is left for the LLM stage.

Confidence is deliberately conservative:
  - password reset / verified account creation -> strong evidence
  - purchase receipts -> weak evidence (guest checkout is common)
  - newsletters alone -> not treated as account evidence at all
"""

from dataclasses import dataclass

from app.gmail.client import MessageSummary
from app.models.evidence import EvidenceType

STRONG_EVIDENCE_TYPES = {
    EvidenceType.PASSWORD_RESET,
    EvidenceType.ACCOUNT_VERIFICATION,
}
WEAK_EVIDENCE_TYPES = {
    EvidenceType.WELCOME_EMAIL,
    EvidenceType.PURCHASE_RECEIPT,
    EvidenceType.SECURITY_NOTICE,
}


@dataclass
class RuleResult:
    matched: bool
    evidence_type: EvidenceType | None
    confidence: int | None
    reason: str | None


# Keyword sets per evidence type, checked against subject + snippet.
_KEYWORDS: dict[EvidenceType, list[str]] = {
    EvidenceType.PASSWORD_RESET: ["reset your password", "password reset", "reset password"],
    EvidenceType.ACCOUNT_VERIFICATION: [
        "verify your email", "confirm your email", "confirm your account",
        "account created", "your new account", "verify your account",
    ],
    EvidenceType.WELCOME_EMAIL: ["welcome to", "welcome aboard", "your account is ready"],
    EvidenceType.SECURITY_NOTICE: ["new sign-in", "security alert", "unusual sign-in activity"],
    EvidenceType.PURCHASE_RECEIPT: ["order confirmation", "your order", "your receipt"],
    EvidenceType.NEWSLETTER: ["newsletter", "unsubscribe"],
}

_CONFIDENCE_BY_TYPE: dict[EvidenceType, int] = {
    EvidenceType.PASSWORD_RESET: 95,
    EvidenceType.ACCOUNT_VERIFICATION: 90,
    EvidenceType.WELCOME_EMAIL: 65,
    EvidenceType.SECURITY_NOTICE: 55,
    EvidenceType.PURCHASE_RECEIPT: 35,
    EvidenceType.NEWSLETTER: 0,  # never treated as account evidence by itself
}


def classify_with_rules(message: MessageSummary) -> RuleResult:
    text = f"{message.subject} {message.snippet}".lower()

    # Check strong/high-confidence types first so a message matching both a
    # strong and a weak keyword set is classified by the stronger signal.
    ordered_types = [
        EvidenceType.PASSWORD_RESET,
        EvidenceType.ACCOUNT_VERIFICATION,
        EvidenceType.WELCOME_EMAIL,
        EvidenceType.SECURITY_NOTICE,
        EvidenceType.PURCHASE_RECEIPT,
        EvidenceType.NEWSLETTER,
    ]

    for evidence_type in ordered_types:
        keywords = _KEYWORDS[evidence_type]
        if any(keyword in text for keyword in keywords):
            if evidence_type == EvidenceType.NEWSLETTER:
                return RuleResult(
                    matched=True,
                    evidence_type=EvidenceType.NEWSLETTER,
                    confidence=0,
                    reason="Newsletter/marketing email; does not by itself indicate an account.",
                )
            return RuleResult(
                matched=True,
                evidence_type=evidence_type,
                confidence=_CONFIDENCE_BY_TYPE[evidence_type],
                reason=f"Subject/snippet matched a known '{evidence_type.value}' pattern.",
            )

    # No confident rule match - defer to the LLM stage.
    return RuleResult(matched=False, evidence_type=None, confidence=None, reason=None)
