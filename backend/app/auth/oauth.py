"""
Google OAuth 2.0 flow, scoped to read-only Gmail access.

We use the `google-auth-oauthlib` flow rather than hand-rolling OAuth. Only
the gmail.readonly scope is ever requested - if Google returns broader
grants than we asked for, we treat that as an error rather than silently
accepting elevated access.
"""

from datetime import datetime, timedelta, timezone

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from app.config import get_settings


def _client_config() -> dict:
    settings = get_settings()
    return {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }


def build_authorization_url(state: str) -> str:
    """Return the Google consent screen URL the frontend should redirect to."""
    settings = get_settings()
    flow = Flow.from_client_config(
        _client_config(),
        scopes=settings.gmail_scopes,
        redirect_uri=settings.google_redirect_uri,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",   # required to receive a refresh token
        include_granted_scopes="false",
        prompt="consent",        # force refresh token issuance every time
        state=state,
    )
    return auth_url


def exchange_code_for_credentials(code: str) -> Credentials:
    """Exchange the authorization code from Google's callback for credentials."""
    settings = get_settings()
    flow = Flow.from_client_config(
        _client_config(),
        scopes=settings.gmail_scopes,
        redirect_uri=settings.google_redirect_uri,
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials

    granted = set(credentials.scopes or [])
    expected = set(settings.gmail_scopes)
    if not granted.issubset(expected):
        # Defensive check: never proceed if Google somehow granted more than
        # the minimal read-only scope we asked for.
        raise PermissionError(f"Unexpected OAuth scopes granted: {granted - expected}")

    return credentials


def credentials_expiry(credentials: Credentials) -> datetime:
    if credentials.expiry:
        return credentials.expiry.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) + timedelta(minutes=55)
