# app/api/deps/admin.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.models.user import User


async def require_admin(
    db: AsyncSession = Depends(get_db),
    x_user_id: str | None = None,  # temp: passed via header
):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    user = await db.get(User, x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user
