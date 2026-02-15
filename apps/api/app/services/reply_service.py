from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.core.models.post import Post
from app.core.models.reply import Reply
from app.core.enums import ContentStatus
from app.services.notification_service import create_notification
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.constants.notification import NotificationType
from app.services.mention_service import extract_mentioned_user_ids
from sqlalchemy import func
from app.core.models.reply_like import ReplyLike



async def create_reply(
    db: AsyncSession,
    *,
    post_id: UUID,
    author_id: UUID,
    body: str,
    parent_id: UUID | None = None,
):
    # -----------------------------
    # Validate post
    # -----------------------------
    post = await db.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")
    if post.status != ContentStatus.active:
        raise ValueError("Replies are disabled for this post")

    # -----------------------------
    # Validate parent reply (if any)
    # -----------------------------
    parent_reply = None
    parent_reply_id = None

    if parent_id:
        parent_reply = await db.get(Reply, parent_id)
        if not parent_reply:
            raise ValueError("Parent reply not found")
        if parent_reply.post_id != post_id:
            raise ValueError("Parent reply does not belong to this post")
        parent_reply_id = parent_reply.id

    # -----------------------------
    # Create reply
    # -----------------------------
    reply = Reply(
        post_id=post_id,
        parent_reply_id=parent_reply_id,
        author_id=author_id,
        body=body,
    )

    db.add(reply)
    await db.commit()
    await db.refresh(reply)

    # -----------------------------
    # 🔔 Reply → Post author
    # -----------------------------
    if parent_reply_id is None:
        if post.author_id != author_id:
            await create_notification(
                db,
                user_id=post.author_id,
                type=NotificationType.POST_REPLY,
                payload={
                    "post_id": str(post.id),
                    "reply_id": str(reply.id),
                    "author_id": str(author_id),
                },
            )

    # -----------------------------
    # 🔔 Reply → Reply author
    # -----------------------------
    if parent_reply and parent_reply.author_id != author_id:
        await create_notification(
            db,
            user_id=parent_reply.author_id,
            type=NotificationType.REPLY_REPLY,
            payload={
                "post_id": str(post.id),
                "parent_reply_id": str(parent_reply.id),
                "reply_id": str(reply.id),
                "author_id": str(author_id),
            },
        )

    # -----------------------------
    # 🔔 Mentions (@username)
    # -----------------------------
    mentioned_user_ids = await extract_mentioned_user_ids(db, body)

    for mentioned_user_id in mentioned_user_ids:
        if mentioned_user_id == author_id:
            continue

        await create_notification(
            db,
            user_id=mentioned_user_id,
            type=NotificationType.MENTION,
            payload={
                "post_id": str(post.id),
                "reply_id": str(reply.id),
                "author_id": str(author_id),
            },
        )

    return reply

async def get_replies_for_post(
    db: AsyncSession,
    post_id: UUID,
    *,
    status: Optional[ContentStatus] = ContentStatus.active,
    limit: int = 20,
    offset: int = 0,
    load_children: bool = False,
) -> List[Reply]:
    stmt = (
        select(
            Reply,
            func.count(ReplyLike.id).label("like_count")
        )
        .outerjoin(ReplyLike, ReplyLike.reply_id == Reply.id)
        .where(
            Reply.post_id == post_id,
            Reply.parent_reply_id == None
        )
        .group_by(Reply.id)
        .order_by(Reply.created_at)
        .limit(limit)
        .offset(offset)
    )

    if status:
        stmt = stmt.where(Reply.status == status)

    result = await db.execute(stmt)
    rows = result.all()

    replies = []
    for reply, like_count in rows:
        reply.like_count = like_count
        replies.append(reply)

    if load_children:
        for reply in replies:
            reply.children = await _load_children(db, reply.id, status)
    else:
        for reply in replies:
            reply.children = None

    return replies

async def _load_children(
    db: AsyncSession,
    parent_id: UUID,
    status: Optional[ContentStatus] = ContentStatus.active,
    limit: int = 20,
    offset: int = 0,
) -> List[Reply]:

    stmt = (
        select(
            Reply,
            func.count(ReplyLike.id).label("like_count")
        )
        .outerjoin(ReplyLike, ReplyLike.reply_id == Reply.id)
        .where(Reply.parent_reply_id == parent_id)
        .group_by(Reply.id)
        .order_by(Reply.created_at)
        .limit(limit)
        .offset(offset)
    )

    if status:
        stmt = stmt.where(Reply.status == status)

    result = await db.execute(stmt)
    rows = result.all()

    children = []
    for child, like_count in rows:
        child.like_count = like_count
        children.append(child)

    for child in children:
        child.children = await _load_children(db, child.id, status, limit, offset)

    return children

async def get_reply_children(
    db: AsyncSession,
    parent_reply_id: UUID,
    *,
    limit: int = 50,
    offset: int = 0,
    status: ContentStatus = ContentStatus.active,
) -> List[Reply]:
    """
    Fetch direct children of a given reply with pagination.
    """
    # Fetch only direct children
    return await get_replies_for_post(
        db,
        post_id=None,  # post_id not needed, filtering by parent_reply_id
        limit=limit,
        offset=offset,
        status=status,
        load_children=False,  # only fetch one level
    )

async def get_children_for_reply(
    db: AsyncSession,
    parent_reply_id: UUID,
    *,
    limit: int = 20,
    offset: int = 0,
    status: Optional[ContentStatus] = ContentStatus.active,
) -> List[Reply]:

    stmt = (
        select(
            Reply,
            func.count(ReplyLike.id).label("like_count")
        )
        .outerjoin(ReplyLike, ReplyLike.reply_id == Reply.id)
        .where(Reply.parent_reply_id == parent_reply_id)
        .group_by(Reply.id)
        .order_by(Reply.created_at)
        .limit(limit)
        .offset(offset)
    )

    if status:
        stmt = stmt.where(Reply.status == status)

    result = await db.execute(stmt)
    rows = result.all()

    children = []
    for child, like_count in rows:
        child.like_count = like_count
        child.children = None
        children.append(child)

    return children
