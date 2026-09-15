"""
/auth routes: kick off Google OAuth and handle the callback.

The frontend never talks to Google directly - it only calls these two
backend endpoints. This keeps the client secret and token exchange fully
server-side.
"""

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.oauth import build_authorization_url, exchange_code_for_credentials, credentials_expiry
from app.auth.tokens import encrypt_token
from app.config import get_settings
from app.db import get_db
from app.models import User, OAuthToken

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
async def google_login(request: Request):
    """Redirect the user to Google's consent screen."""
    state = secrets.token_urlsafe(24)
    request.session["oauth_state"] = state
    auth_url = build_authorization_url(state=state)
    return RedirectResponse(auth_url)


@router.get("/google/callback")
async def google_callback(request: Request, code: str, state: str, db: AsyncSession = Depends(get_db)):
    """Handle Google's redirect back, exchange the code, and persist tokens."""
    expected_state = request.session.pop("oauth_state", None)
    if not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    credentials = exchange_code_for_credentials(code)

    # google-auth doesn't return the user's email directly; a lightweight
    # userinfo call (or decoding the id_token) is needed to identify them.
    # Left as a call to a small helper so it's easy to swap/test.
    from app.auth.userinfo import get_verified_email

    email = get_verified_email(credentials)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(email=email)
        db.add(user)
        await db.flush()

    # oauth_tokens.user_id has a unique constraint - one token record per
    # user, by design. On reconnect, update the existing row instead of
    # inserting a second one (which would violate that constraint).
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user.id))
    existing_token = result.scalar_one_or_none()

    encrypted_access_token = encrypt_token(credentials.token)
    expires_at = credentials_expiry(credentials)

    # Google only returns a refresh_token on some authorizations (typically
    # the first consent, or subsequent ones only if the flow forces
    # prompt=consent, which build_authorization_url already does - but we
    # stay defensive here in case Google omits it on a given reconnect).
    # Never overwrite a valid stored refresh token with nothing.
    if credentials.refresh_token:
        encrypted_refresh_token = encrypt_token(credentials.refresh_token)
    elif existing_token is not None:
        encrypted_refresh_token = existing_token.encrypted_refresh_token
    else:
        # No existing token to fall back on and Google didn't send one -
        # we can't proceed without a refresh token for future scans.
        raise HTTPException(
            status_code=400,
            detail="Google did not return a refresh token. Please reconnect and grant access again.",
        )

    if existing_token is not None:
        existing_token.encrypted_access_token = encrypted_access_token
        existing_token.encrypted_refresh_token = encrypted_refresh_token
        existing_token.expires_at = expires_at
    else:
        db.add(
            OAuthToken(
                user_id=user.id,
                encrypted_access_token=encrypted_access_token,
                encrypted_refresh_token=encrypted_refresh_token,
                expires_at=expires_at,
            )
        )

    await db.commit()

    request.session["user_id"] = str(user.id)

    settings = get_settings()
    return RedirectResponse(f"{settings.frontend_base_url}/scan")
