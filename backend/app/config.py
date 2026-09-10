"""
Central application settings.

All secrets and environment-specific values come from environment variables.
Nothing here should ever contain a real secret - see .env.example for the
variables you need to set locally.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "Footprint"
    environment: str = "development"
    frontend_base_url: str = "http://localhost:5173"
    backend_base_url: str = "http://localhost:8000"

    # --- Database ---
    database_url: str  # e.g. postgresql+asyncpg://user:pass@localhost:5432/footprint

    # --- Security ---
    # Fernet key used to encrypt OAuth tokens at rest. Generate with:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    token_encryption_key: str
    session_secret: str  # used to sign session/JWT cookies

    # --- Google OAuth / Gmail API ---
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    # Minimum permissions necessary: openid+email only to reliably identify
    # which Google account was connected (so we don't have to trust a
    # manually-typed email that could mismatch the authorized inbox), and
    # gmail.readonly to scan for account-related emails. No broader profile,
    # send, modify, or delete permissions are ever requested.
    gmail_scopes: list[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    # --- LLM provider (used only for ambiguous email classification) ---
    llm_provider: str = "anthropic"  # swappable: "anthropic", "openai", etc.
    anthropic_api_key: str | None = None
    llm_model: str = "claude-sonnet-4-6"

    # --- Ghost account heuristic ---
    # An account with no evidence newer than this many days is a candidate
    # "ghost" account (default: ~2 years).
    ghost_inactivity_days: int = 730


@lru_cache
def get_settings() -> Settings:
    """Settings are cached so the .env file is only parsed once per process."""
    return Settings()
