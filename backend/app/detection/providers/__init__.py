from app.config import get_settings
from app.detection.llm_client import LLMClassifier


def get_llm_classifier() -> LLMClassifier:
    """
    Single place that decides which LLM provider implementation to use.
    Add new providers as sibling modules and register them here.
    """
    settings = get_settings()
    if settings.llm_provider == "anthropic":
        from .anthropic_provider import AnthropicLLMClassifier
        return AnthropicLLMClassifier()
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
