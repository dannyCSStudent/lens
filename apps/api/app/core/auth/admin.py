# app/core/auth/admin.py

from fastapi import Depends, HTTPException
from app.core.auth.dependencies import get_current_user
from app.core.models import User


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
