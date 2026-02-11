from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from sqlalchemy import func
from app.core.models.notification import Notification
from fastapi import HTTPException


# -------------------------
# Create notification
# -------------------------
async def create_notification(
    db: AsyncSession,
    *,
    user_id: UUID,
    type: str,
    payload: dict,
    commit: bool = True,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        payload=payload,
    )
    db.add(notification)

    if commit:
        await db.commit()
        await db.refresh(notification)

    return notification


    

    


# -------------------------
# Fetch notifications
# -------------------------
async def get_user_notifications(
    db: AsyncSession,
    user_id: UUID,
    *,
    limit: int = 20,
    offset: int = 0,
):
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


# -------------------------
# Unread count
# -------------------------
async def get_unread_count(
    db: AsyncSession,
    user_id: UUID,
) -> int:
    stmt = select(func.count()).select_from(Notification).where(
        Notification.user_id == user_id,
        Notification.read_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one()


# -------------------------
# Mark as read
# -------------------------
async def mark_notification_read(
    db: AsyncSession,
    *,
    notification_id: UUID,
    user_id: UUID,
) -> None:
    stmt = (
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
        .values(read_at=datetime.utcnow())
        .returning(Notification.id)
    )

    result = await db.execute(stmt)
    updated = result.scalar_one_or_none()

    if not updated:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.commit()

