from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import Account, EmailEvidence, User
from app.schemas.account import AccountOut, EvidenceOut

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
async def list_accounts(
    ghosts_only: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Account).where(Account.user_id == user.id)
    if ghosts_only:
        query = query.where(Account.is_ghost.is_(True))
    result = await db.execute(query.order_by(Account.last_evidence_at.desc()))
    return result.scalars().all()


@router.get("/{account_id}/evidence", response_model=list[EvidenceOut])
async def get_account_evidence(
    account_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the explainable evidence trail behind a single account."""
    result = await db.execute(
        select(EmailEvidence)
        .where(EmailEvidence.account_id == account_id, EmailEvidence.user_id == user.id)
        .order_by(EmailEvidence.email_date.asc())
    )
    return result.scalars().all()
