"""
Fetch the authenticated user's verified email address.

We request only the 'openid' and 'email' scopes for this - never profile,
name, or photo - because automatically identifying the connected Gmail
account (rather than trusting a manually typed email) avoids a mismatch
between what the user types and which inbox they actually authorized.
"""

import requests
from google.oauth2.credentials import Credentials

_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


def get_verified_email(credentials: Credentials) -> str:
    response = requests.get(
        _USERINFO_ENDPOINT,
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    email = payload.get("email")
    email_verified = payload.get("email_verified")
    if not email or not email_verified:
        raise ValueError("Google did not return a verified email address")
    return email
