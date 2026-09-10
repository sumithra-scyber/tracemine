"""
Anthropic-backed implementation of LLMClassifier.

Uses structured JSON output via prompting. If you swap to a different
provider, implement the same LLMClassifier interface in a sibling module and
point get_llm_classifier() (in providers/__init__.py) at it - nothing else
in the codebase changes.
"""

import json

import anthropic

from app.config import get_settings
from app.detection.llm_client import LLMClassifier, LLMClassificationResult

_SYSTEM_PROMPT = """You classify a single email header/snippet to judge whether it is \
evidence that the recipient has an account on some online platform.

Respond with ONLY a JSON object, no other text, in this exact shape:
{"classification": "ACCOUNT_EVIDENCE" or "NOT_ACCOUNT_EVIDENCE", \
"confidence": <integer 0-100>, "reason": "<one short sentence>", \
"platform": "<platform/company name, or null if unclear>"}

Guidelines:
- Be conservative. A newsletter or marketing email alone is NOT account evidence.
- A purchase receipt is weak evidence at most (guest checkout is common) - confidence should reflect that.
- Only mark high confidence when the content clearly implies account creation, verification, or account-specific security activity.
"""


class AnthropicLLMClassifier(LLMClassifier):
    def __init__(self):
        settings = get_settings()
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.llm_model

    def classify(self, sender_domain: str, subject: str, snippet: str) -> LLMClassificationResult:
        user_content = (
            f"Sender domain: {sender_domain}\n"
            f"Subject: {subject}\n"
            f"Snippet: {snippet}"
        )
        response = self._client.messages.create(
            model=self._model,
            max_tokens=200,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        raw_text = "".join(block.text for block in response.content if block.type == "text")
        parsed = json.loads(raw_text)

        return LLMClassificationResult(
            classification=parsed["classification"],
            confidence=int(parsed["confidence"]),
            reason=parsed["reason"],
            platform=parsed.get("platform"),
        )
