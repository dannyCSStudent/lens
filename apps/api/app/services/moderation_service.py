# app/services/moderation_service.py

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.post import Post
from app.core.models.reply import Reply
from app.core.models.moderation import ModerationAction
from app.core.enums import ContentStatus


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

    return target
