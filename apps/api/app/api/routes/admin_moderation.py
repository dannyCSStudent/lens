# app/api/routes/admin_moderation.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import Query, HTTPException
from typing import List
from app.core.models.user import User
from app.api.schemas.moderation import ModerationActionRead
from app.services.moderation_service import get_moderation_history
from app.api.deps.admin import require_admin
from app.api.schemas.moderation import ModerateRequest
from app.services.moderation_service import moderate_content
from app.core.database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.post("")
async def moderate(
    data: ModerateRequest,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    result = await moderate_content(
        db,
        moderator_id=admin.id,
        target_type=data.target_type,
        target_id=data.target_id,
        new_status=data.new_status,
        reason=data.reason,
    )

    return {
        "success": True,
        "target_type": data.target_type,
        "target_id": data.target_id,
        "new_status": data.new_status,
    }


async def get_current_user(x_user_id: UUID = Query(...), db: AsyncSession = Depends(get_db)) -> User:
    user = await db.get(User, x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/moderation/history", response_model=List[ModerationActionRead])
async def moderation_history(
    moderator_id: UUID | None = Query(None),
    target_type: str | None = Query(None),
    target_id: UUID | None = Query(None),
    status: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    actions = await get_moderation_history(
        db,
        moderator_id=moderator_id,
        target_type=target_type,
        target_id=target_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return actions
