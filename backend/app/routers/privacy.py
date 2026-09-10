"""
Privacy controls: let a user fully delete their Footprint data on demand.

Deleting the User row cascades (via ondelete="CASCADE" on the foreign keys)
to OAuthToken, EmailEvidence, and Account - so one action removes everything
we hold about them, including their encrypted Gmail tokens.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.delete("/delete-my-data")
async def delete_my_data(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(user)
    await db.commit()
    return {"status": "deleted"}
