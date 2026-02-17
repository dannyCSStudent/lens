from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.post import PostRead, PostCreate
from app.services.post_service import get_posts
from app.core.database import get_db
from app.core.models.post import Post
from app.services.post_service import get_post_by_id
from fastapi import HTTPException
from uuid import UUID
from app.core.enums import ContentStatus, FeedMode
from app.core.auth.dependencies import get_current_user
from app.core.models.user import User
from app.api.schemas.feed import PostCard, UserPublic




router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=List[PostRead])
async def list_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await get_posts(db, limit=limit, offset=offset)


@router.get("/posts")
async def list_posts(
    mode: str = "latest",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_posts(
        db,
        current_user_id=current_user.id,
        mode=mode,
    )


@router.post("", response_model=PostRead)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(
        title=data.title,
        body=data.body,
        author_id=current_user.id,
        post_type=data.post_type,
        status=ContentStatus.active,
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post


@router.get("/feed", response_model=list[PostCard])
async def get_feed(
    mode: FeedMode = FeedMode.latest,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    posts = await get_posts(
    db,
    mode=mode,
    limit=limit,
    offset=offset,
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
                evidence_count=post.reply_count,  # temp placeholder
                confidence_state="no_review",
                trending_score=post.trending_score,
                author=UserPublic(
                    id=post.author.id,
                    username=post.author.username,
                    display_name=post.author.display_name,
                    bio=post.author.bio,
                )
            )
        )

    return feed



@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post



