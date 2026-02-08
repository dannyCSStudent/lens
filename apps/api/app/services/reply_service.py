from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.core.models.post import Post
from app.core.models.reply import Reply
from app.core.enums import ContentStatus


async def create_reply(
    db: AsyncSession,
    *,
    post_id,
    author_id,
    body,
    parent_reply_id=None,
):
    post = await db.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")

    if post.status != ContentStatus.active:
        raise ValueError("Replies are disabled for this post")

    if parent_reply_id:
        parent = await db.get(Reply, parent_reply_id)
        if not parent:
            raise ValueError("Parent reply not found")
        if parent.post_id != post_id:
            raise ValueError("Parent reply does not belong to this post")

    reply = Reply(
        post_id=post_id,
        parent_reply_id=parent_reply_id,
        author_id=author_id,
        body=body,
    )

    db.add(reply)
    await db.commit()
    await db.refresh(reply)

    return reply


async def get_replies_for_post(
    db: AsyncSession,
    post_id: UUID,
) -> list[Reply]:
    # Ensure post exists
    post = await db.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")

    # Optional: disallow reading replies for removed content
    if post.status == ContentStatus.removed_illegal:
        return []

    result = await db.execute(
        select(Reply)
        .where(
            Reply.post_id == post_id,
            Reply.status == ContentStatus.active,
        )
        .order_by(Reply.created_at.asc())
    )

    return result.scalars().all()