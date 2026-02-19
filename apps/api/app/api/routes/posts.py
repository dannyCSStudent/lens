from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.schemas.post import PostRead, PostCreate
from app.api.schemas.feed import PostCard, UserPublic
from app.services.post_service import get_feed, get_post_by_id
from app.core.database import get_db
from app.core.models.post import Post
from app.core.models.user import User
from app.core.enums import ContentStatus, FeedMode
from app.core.auth.dependencies import get_current_user, get_optional_user


router = APIRouter(prefix="/posts", tags=["posts"])


# 🔓 Public feed (user optional)
@router.get("/feed", response_model=dict)
async def get_feed_route(
    mode: FeedMode = FeedMode.latest,
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    posts, next_cursor = await get_feed(
        db,
        mode=mode,
        limit=limit,
        cursor=cursor,
        current_user_id=current_user.id if current_user else None,
    )

    feed = []

    for post in posts:
        feed.append(
            PostCard(
                id=post.id,
                post_type=post.post_type,
                title=post.title,
                created_at=post.created_at,
                status=post.status,
                evidence_count=post.reply_count,
                confidence_state="no_review",
                trending_score=post.trending_score,
                like_count=post.like_count,
                reply_count=post.reply_count,
                has_liked=post.liked_by_current_user,
                author=UserPublic(
                    id=post.author.id,
                    username=post.author.username,
                    display_name=post.author.display_name,
                    bio=post.author.bio,
                ),
            )
        )

    return {
        "items": feed,
        "next_cursor": next_cursor,
    }


# 🔓 Public single post
@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post
