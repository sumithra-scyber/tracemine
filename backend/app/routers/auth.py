"""
/auth routes: kick off Google OAuth and handle the callback.

The frontend never talks to Google directly - it only calls these two
backend endpoints. This keeps the client secret and token exchange fully
server-side.
"""

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
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

    result = await db.execute(User.__table__.select().where(User.email == email))
    user_row = result.first()

    if user_row is None:
        user = User(email=email)
        db.add(user)
        await db.flush()
    else:
        user = user_row

    token = OAuthToken(
        user_id=user.id,
        encrypted_access_token=encrypt_token(credentials.token),
        encrypted_refresh_token=encrypt_token(credentials.refresh_token),
        expires_at=credentials_expiry(credentials),
    )
    db.add(token)
    await db.commit()

    request.session["user_id"] = str(user.id)

    settings = get_settings()
    return RedirectResponse(f"{settings.frontend_base_url}/scan")
