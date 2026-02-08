from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.models.user import User
from sqlalchemy import select


async def get_current_user(
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    TEMP: always returns the first user.
    Replace with real auth later.
    """
    result = await db.execute(
        select(User).limit(1)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="No users exist (auth stub)",
        )

    return user
