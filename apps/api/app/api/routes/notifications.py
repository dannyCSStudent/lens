from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from typing import List
from uuid import UUID

from app.api.schemas.notification import NotificationRead
from app.services.notification_service import (
    get_user_notifications,
    mark_notification_read,
    get_unread_count,
)
from app.core.database import get_db
from app.core.auth.dependencies import get_current_user
from app.core.models.user import User
from app.core.models.notification import Notification
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationRead])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await get_user_notifications(
        db,
        user.id,
        limit=limit,
        offset=offset,
    )


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    count = await get_unread_count(db, user.id)
    return {"count": count}


@router.post("/{notification_id}/read")
async def read_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await mark_notification_read(
        db,
        notification_id=notification_id,
        user_id=user.id,
    )
    return {"ok": True}


@router.post("/read-all")
async def read_all_notifications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == user.id,
            Notification.read_at.is_(None),
        )
        .values(read_at=datetime.utcnow())
    )

    await db.execute(stmt)
    await db.commit()

    return {"ok": True}
