from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import auth, scan, accounts, privacy

settings = get_settings()

app = FastAPI(title=settings.app_name)

# Signed session cookie used to track the logged-in user and OAuth state.
# Uses SESSION_SECRET, distinct from the token encryption key.
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, same_site="lax")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(accounts.router)
app.include_router(privacy.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
