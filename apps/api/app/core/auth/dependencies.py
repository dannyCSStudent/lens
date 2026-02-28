from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from uuid import UUID
from app.core.database import get_db
from app.core.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM
from datetime import datetime, timezone
from app.core.cache.redis import redis_client



async def get_current_user(
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
) -> User:

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str | None = payload.get("sub")
        token_sid: str | None = payload.get("sid")

        if not user_id or not token_sid:
            raise HTTPException(status_code=401, detail="Invalid token")

        # 🚨 Instant access-token revocation check (Redis)
        if await redis_client.get(f"revoked:{token_sid}"):
            raise HTTPException(
                status_code=401,
                detail="Session revoked"
            )

        user_uuid = UUID(user_id)

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 🔐 Enforce email verification
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified"
        )

    # 🔒 Lockout check
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=403,
            detail="Account locked"
        )

    return user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
) -> User | None:

    if not access_token:
        return None

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        token_sid = payload.get("sid")

        if not user_id or not token_sid:
            return None

        # 🚨 Instant session revoke check
        if await redis_client.get(f"revoked:{token_sid}"):
            return None

        user_uuid = UUID(user_id)

        result = await db.execute(
            select(User).where(User.id == user_uuid)
        )
        return result.scalar_one_or_none()

    except Exception:
        return None
