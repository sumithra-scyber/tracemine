import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from google.oauth2.credentials import Credentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.tokens import decrypt_token
from app.config import get_settings
from app.db import get_db, async_session_factory
from app.gmail.client import GmailClient
from app.models import OAuthToken, User
from app.models.scan_job import ScanJob
from app.schemas.scan import ScanJobOut
from app.services.scan_service import run_scan

router = APIRouter(prefix="/scan", tags=["scan"])


async def _load_credentials(db: AsyncSession, user: User) -> Credentials:
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user.id))
    token = result.scalar_one_or_none()
    if token is None:
        raise HTTPException(status_code=400, detail="Gmail is not connected for this account")

    settings = get_settings()
    return Credentials(
        token=decrypt_token(token.encrypted_access_token),
        refresh_token=decrypt_token(token.encrypted_refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=settings.gmail_scopes,
    )


async def _run_scan_with_own_session(user_id: uuid.UUID, gmail_client: GmailClient, scan_job_id: uuid.UUID) -> None:
    """
    Background tasks execute after the request's own DB session has already
    been closed, so this opens a fresh session scoped to the task itself
    rather than reusing the request-scoped one from Depends(get_db).
    """
    async with async_session_factory() as session:
        await run_scan(session, user_id, gmail_client, scan_job_id)


@router.post("/start", response_model=ScanJobOut)
async def start_scan(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    credentials = await _load_credentials(db, user)
    gmail_client = GmailClient(credentials)

    job = ScanJob(user_id=user.id)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Runs in the background so the frontend can poll /scan/status instead of
    # holding one long HTTP request open. No WebSockets for the MVP.
    background_tasks.add_task(_run_scan_with_own_session, user.id, gmail_client, job.id)
    return job


@router.get("/status/{scan_job_id}", response_model=ScanJobOut)
async def get_scan_status(
    scan_job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanJob).where(ScanJob.id == scan_job_id, ScanJob.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return job
