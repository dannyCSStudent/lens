from sqlalchemy import select, func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.core.enums import ContentStatus
from app.core.models.post import Post
from app.core.models.post_like import PostLike
from app.core.models.reply import Reply


async def get_posts(
    db: AsyncSession,
    *,
    current_user_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0,
    mode: str = "latest",
):
    # Like count
    like_count_subq = (
        select(func.count(PostLike.id))
        .where(PostLike.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    # Reply count
    reply_count_subq = (
        select(func.count(Reply.id))
        .where(Reply.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    # Engagement score
    engagement_score = (
        (like_count_subq * 2) +
        (reply_count_subq * 3)
    )

    # Hours since posted
    hours_since_posted = (
        extract("epoch", func.now() - Post.created_at) / 3600
    )

    # Time-decay trending score
    trending_score = (
        engagement_score / (hours_since_posted + 2)
    ).label("trending_score")



    # Liked by current user
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
        trending_score,
    ]

    if liked_subq is not None:
        columns.append(liked_subq.label("liked_by_current_user"))

    # Correct ordering
    if mode == "trending":
        order_clause = trending_score.desc()
    else:
        order_clause = Post.created_at.desc()

    stmt = (
        select(*columns)
        .where(Post.status == ContentStatus.active)
        .order_by(order_clause)   # ✅ FIXED
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    rows = result.all()

    posts = []

    for row in rows:
        if current_user_id:
            post, like_count, reply_count, trending_score_val, liked_by_current_user = row
            post.liked_by_current_user = liked_by_current_user
        else:
            post, like_count, reply_count, trending_score_val = row
            post.liked_by_current_user = False

        post.like_count = like_count or 0
        post.reply_count = reply_count or 0
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
