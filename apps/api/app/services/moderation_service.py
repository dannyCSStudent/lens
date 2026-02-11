from uuid import UUID
from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.models.post import Post
from app.core.models.reply import Reply
from app.core.models.moderation import ModerationAction
from app.core.enums import ContentStatus
from app.api.schemas.moderation import (
    ModerationActionType,
    ModerationTargetType,
)
from app.services.notification_service import create_notification


async def moderate_content(
    db: AsyncSession,
    *,
    moderator_id: UUID,
    target_type: str,  # "post" | "reply"
    target_id: UUID,
    new_status: ContentStatus,
    reason: str | None = None,
):
    if target_type == "post":
        target = await db.get(Post, target_id)
    elif target_type == "reply":
        target = await db.get(Reply, target_id)
    else:
        raise ValueError("Invalid target type")

    if not target:
        raise ValueError("Target not found")

    previous_status = target.status

    if previous_status == new_status:
        return target  # no-op

    target.status = new_status

    action = ModerationAction(
        moderator_id=moderator_id,
        target_type=target_type,
        target_id=target_id,
        previous_status=previous_status,
        new_status=new_status,
        reason=reason,
    )

    db.add(action)
    await db.commit()
    await db.refresh(target)

    # -----------------------------
    # 🔔 Notify content author
    # -----------------------------
    if hasattr(target, "author_id") and target.author_id != moderator_id:
        await create_notification(
            db,
            user_id=target.author_id,
            type="content_moderated",
            payload={
                "target_type": target_type,
                "target_id": str(target_id),
                "previous_status": previous_status,
                "new_status": new_status,
                "reason": reason,
            },
        )

    return target


async def get_moderation_history(
    db: AsyncSession,
    *,
    moderator_id: UUID | None = None,
    target_type: ModerationTargetType | None = None,
    target_id: UUID | None = None,
    status: ModerationActionType | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> List[ModerationAction]:
    query = select(ModerationAction)

    if moderator_id:
        query = query.where(ModerationAction.moderator_id == moderator_id)
    if target_type:
        query = query.where(ModerationAction.target_type == target_type)
    if target_id:
        query = query.where(ModerationAction.target_id == target_id)
    if status:
        query = query.where(ModerationAction.action == status)
    if start_date:
        query = query.where(ModerationAction.created_at >= start_date)
    if end_date:
        query = query.where(ModerationAction.created_at <= end_date)

    query = (
        query.order_by(ModerationAction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    return result.scalars().all()
