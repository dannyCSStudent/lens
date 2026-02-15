from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from app.core.models.post_like import PostLike
from app.core.models.reply_like import ReplyLike
from app.core.models.post import Post
from app.core.models.reply import Reply
from app.services.notification_service import create_notification
from app.core.constants.notification import NotificationType


# ---------------------
# Like Post
# ---------------------
async def like_post(db: AsyncSession, *, post_id: UUID, user_id: UUID):
    post = await db.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")

    like = PostLike(post_id=post_id, user_id=user_id)
    db.add(like)

    try:
        await db.commit()
        created = True
    except IntegrityError:
        await db.rollback()
        created = False  # already liked

    # Only notify if it was actually newly created
    if created and post.author_id != user_id:
        await create_notification(
            db,
            user_id=post.author_id,
            type=NotificationType.POST_LIKE,
            payload={
                "post_id": str(post_id),
                "author_id": str(user_id),
            },
        )

    return created


# ---------------------
# Unlike Post
# ---------------------
async def unlike_post(db: AsyncSession, *, post_id: UUID, user_id: UUID):
    stmt = delete(PostLike).where(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id,
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0


# ---------------------
# Like Reply
# ---------------------
async def like_reply(db: AsyncSession, *, reply_id: UUID, user_id: UUID):
    reply = await db.get(Reply, reply_id)
    if not reply:
        raise ValueError("Reply not found")

    like = ReplyLike(reply_id=reply_id, user_id=user_id)
    db.add(like)

    try:
        await db.commit()
        created = True
    except IntegrityError:
        await db.rollback()
        created = False

    if created and reply.author_id != user_id:
        await create_notification(
            db,
            user_id=reply.author_id,
            type=NotificationType.REPLY_LIKE,
            payload={
                "reply_id": str(reply_id),
                "author_id": str(user_id),
            },
        )

    return created


# ---------------------
# Unlike Reply
# ---------------------
async def unlike_reply(db: AsyncSession, *, reply_id: UUID, user_id: UUID):
    stmt = delete(ReplyLike).where(
        ReplyLike.reply_id == reply_id,
        ReplyLike.user_id == user_id,
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0
