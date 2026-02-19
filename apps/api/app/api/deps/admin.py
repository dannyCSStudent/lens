from fastapi import Depends, HTTPException, status
from app.core.auth.dependencies import get_current_user
from app.core.models.user import User


async def require_admin(
    current_user: User = Depends(get_current_user),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user
