from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError

from app.core.models.post_likes import PostLike
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
        # Flush first to trigger unique constraint
        await db.flush()

        # 🔥 Atomic increment (safe under concurrency)
        await db.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(like_count=Post.like_count + 1)
        )

        await db.commit()
        created = True

    except IntegrityError:
        await db.rollback()
        created = False  # already liked

    # 🔔 Notify only if newly created
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
    stmt = (
        delete(PostLike)
        .where(
            PostLike.post_id == post_id,
            PostLike.user_id == user_id,
        )
        .returning(PostLike.id)
    )

    result = await db.execute(stmt)
    deleted = result.first()

    if deleted:
        # 🔥 Atomic decrement (prevents race issues)
        await db.execute(
            update(Post)
            .where(Post.id == post_id, Post.like_count > 0)
            .values(like_count=Post.like_count - 1)
        )

        await db.commit()
        return True

    await db.commit()
    return False


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
        await db.flush()

        # 🔥 Atomic increment
        await db.execute(
            update(Reply)
            .where(Reply.id == reply_id)
            .values(like_count=Reply.like_count + 1)
        )

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
    stmt = (
        delete(ReplyLike)
        .where(
            ReplyLike.reply_id == reply_id,
            ReplyLike.user_id == user_id,
        )
        .returning(ReplyLike.id)
    )

    result = await db.execute(stmt)
    deleted = result.first()

    if deleted:
        await db.execute(
            update(Reply)
            .where(Reply.id == reply_id, Reply.like_count > 0)
            .values(like_count=Reply.like_count - 1)
        )

        await db.commit()
        return True

    await db.commit()
    return False
