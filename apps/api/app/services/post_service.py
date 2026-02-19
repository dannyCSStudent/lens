from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.post import Post
from app.core.models.user import User
from app.core.models.post_likes import PostLike
from app.core.models.reply import Reply
from app.core.enums import FeedMode, ContentStatus

from sqlalchemy import select, func, extract, or_, and_
from typing import Optional
from datetime import datetime




async def get_feed(
    db: AsyncSession,
    *,
    current_user_id: Optional[UUID] = None,
    limit: int = 20,
    cursor: Optional[str] = None,
    mode: FeedMode = FeedMode.latest,
):
    stmt = (
        select(Post, User)
        .join(User, User.id == Post.author_id)
        .where(Post.status == ContentStatus.active)
    )

    # -------------------------
    # Trending calculation
    # -------------------------

    engagement_score = func.log(
        (Post.like_count * 2)
        + (Post.reply_count * 3)
        + 1
    )

    hours_since_posted = (
        extract("epoch", func.now() - Post.created_at) / 3600
    )

    trending_score = (
        engagement_score /
        func.pow(hours_since_posted + 2, 1.1)
    ).label("trending_score")

    stmt = stmt.add_columns(trending_score)

    # -------------------------
    # liked_by_current_user
    # -------------------------

    if current_user_id:
        liked_exists = (
            select(1)
            .where(
                PostLike.post_id == Post.id,
                PostLike.user_id == current_user_id,
            )
            .exists()
        ).label("liked_by_current_user")

        stmt = stmt.add_columns(liked_exists)

    # -------------------------
    # Cursor filtering (LATEST ONLY)
    # -------------------------

    if mode == FeedMode.latest:
        stmt = stmt.order_by(
            Post.created_at.desc(),
            Post.id.desc(),
        )

        if cursor:
            cursor_created_at_str, cursor_id = cursor.split("|")
            cursor_created_at = datetime.fromisoformat(
                cursor_created_at_str
            )

            stmt = stmt.where(
                or_(
                    Post.created_at < cursor_created_at,
                    and_(
                        Post.created_at == cursor_created_at,
                        Post.id < cursor_id,
                    ),
                )
            )

    elif mode == FeedMode.trending:
        stmt = stmt.order_by(trending_score.desc())

        # Optional: you can later build cursor pagination for trending too

    stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    posts = []

    for row in rows:
        if current_user_id:
            post, user, trending_score_val, liked_val = row
            post.liked_by_current_user = liked_val or False
        else:
            post, user, trending_score_val = row
            post.liked_by_current_user = False

        post.author = user
        post.trending_score = trending_score_val or 0

        posts.append(post)

    # -------------------------
    # Generate next cursor
    # -------------------------

    next_cursor = None

    if posts and mode == FeedMode.latest:
        last_post = posts[-1]
        next_cursor = (
            f"{last_post.created_at.isoformat()}|{last_post.id}"
        )

    return posts, next_cursor


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
        User,
        like_count_subq.label("like_count"),
        reply_count_subq.label("reply_count"),
    ]


    if liked_subq is not None:
        columns.append(liked_subq.label("liked_by_current_user"))

    stmt = (
        select(*columns)
        .join(User, User.id == Post.author_id)
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
        post, user, like_count, reply_count, liked_by_current_user = row
        post.liked_by_current_user = liked_by_current_user
    else:
        post, user, like_count, reply_count = row
        post.liked_by_current_user = False

    post.author = user


    post.like_count = like_count or 0
    post.reply_count = reply_count or 0

    return post
