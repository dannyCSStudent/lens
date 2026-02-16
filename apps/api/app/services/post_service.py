from sqlalchemy import select, func, extract, text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.core.enums import ContentStatus
from app.core.models.post import Post
from app.core.models.post_likes import PostLike
from app.core.models.reply import Reply


from sqlalchemy import select, func, extract, text, case, literal


async def get_posts(
    db: AsyncSession,
    *,
    current_user_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0,
    mode: str = "latest",
):

    # -------------------------
    # Base joins
    # -------------------------
    stmt = (
        select(
            Post,
            func.count(func.distinct(PostLike.id)).label("like_count"),
            func.count(func.distinct(Reply.id)).label("reply_count"),
        )
        .outerjoin(PostLike, PostLike.post_id == Post.id)
        .outerjoin(Reply, Reply.post_id == Post.id)
        .where(Post.status == ContentStatus.active)
        .group_by(Post.id)
    )

    like_count = func.count(func.distinct(PostLike.id))
    reply_count = func.count(func.distinct(Reply.id))

    # -------------------------
    # Trending calculation
    # -------------------------
    engagement_score = func.log(
        (like_count * 2) + (reply_count * 3) + 1
    )

    hours_since_posted = (
        extract("epoch", func.now() - Post.created_at) / 3600
    )

    base_trending_score = (
        engagement_score /
        func.pow(hours_since_posted + 2, 1.5)
    )

    # Use FILTER instead of CASE
    recent_likes = func.count(func.distinct(PostLike.id)).filter(
        PostLike.created_at >= func.now() - text("interval '3 hours'")
    )

    recent_replies = func.count(func.distinct(Reply.id)).filter(
        Reply.created_at >= func.now() - text("interval '3 hours'")
    )

    velocity_score = (recent_likes * 3) + (recent_replies * 4)

    trending_score = (
        base_trending_score + (velocity_score * 0.5)
    ).label("trending_score")

    stmt = stmt.add_columns(trending_score)

    # -------------------------
    # liked_by_current_user
    # -------------------------
    if current_user_id:
        liked_flag = func.bool_or(
            PostLike.user_id == current_user_id
        ).label("liked_by_current_user")

        stmt = stmt.add_columns(liked_flag)

    # -------------------------
    # Ordering
    # -------------------------
    if mode == "trending":
        stmt = stmt.order_by(trending_score.desc())
    else:
        stmt = stmt.order_by(Post.created_at.desc())

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    rows = result.all()

    posts = []

    for row in rows:
        if current_user_id:
            post, like_count_val, reply_count_val, trending_score_val, liked_by_current_user = row
            post.liked_by_current_user = liked_by_current_user or False
        else:
            post, like_count_val, reply_count_val, trending_score_val = row
            post.liked_by_current_user = False

        post.like_count = like_count_val or 0
        post.reply_count = reply_count_val or 0
        post.trending_score = trending_score_val or 0

        posts.append(post)

    return posts


async def get_post_by_id(
    db: AsyncSession,
    post_id: UUID,
    current_user_id: Optional[UUID] = None,
):
    like_count_subq = (
        select(func.count(PostLike.id))
        .where(PostLike.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    reply_count_subq = (
        select(func.count(Reply.id))
        .where(Reply.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    if current_user_id:
        liked_subq = (
            select(PostLike.id)
            .where(
                PostLike.post_id == Post.id,
                PostLike.user_id == current_user_id,
            )
            .correlate(Post)
            .exists()
        )
    else:
        liked_subq = None

    columns = [
        Post,
        like_count_subq.label("like_count"),
        reply_count_subq.label("reply_count"),
    ]

    if liked_subq is not None:
        columns.append(liked_subq.label("liked_by_current_user"))

    stmt = (
        select(*columns)
        .where(
            Post.id == post_id,
            Post.status == ContentStatus.active,
        )
    )

    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return None

    if current_user_id:
        post, like_count, reply_count, liked_by_current_user = row
        post.liked_by_current_user = liked_by_current_user
    else:
        post, like_count, reply_count = row
        post.liked_by_current_user = False

    post.like_count = like_count or 0
    post.reply_count = reply_count or 0

    return post
