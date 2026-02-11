from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.models.user import User
from sqlalchemy import select


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    x_user_id: UUID | None = Header(default=None),
) -> User:
    if x_user_id:
        result = await db.execute(
            select(User).where(User.id == x_user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user

    # fallback (old behavior)
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="No users exist")

    return user
