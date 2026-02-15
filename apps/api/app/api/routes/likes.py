from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user
from app.core.models.user import User
from app.services.like_service import (
    like_post,
    unlike_post,
    like_reply,
    unlike_reply,
)

router = APIRouter(prefix="/likes", tags=["likes"])


# ---------------------
# Post Likes
# ---------------------
@router.post("/posts/{post_id}")
async def like_post_route(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        created = await like_post(db, post_id=post_id, user_id=user.id)
        return {"ok": True, "liked": True, "created": created}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/posts/{post_id}")
async def unlike_post_route(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = await unlike_post(db, post_id=post_id, user_id=user.id)
    return {"ok": True, "liked": False, "deleted": deleted}


# ---------------------
# Reply Likes
# ---------------------
@router.post("/replies/{reply_id}")
async def like_reply_route(
    reply_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        created = await like_reply(db, reply_id=reply_id, user_id=user.id)
        return {"ok": True, "liked": True, "created": created}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/replies/{reply_id}")
async def unlike_reply_route(
    reply_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = await unlike_reply(db, reply_id=reply_id, user_id=user.id)
    return {"ok": True, "liked": False, "deleted": deleted}
