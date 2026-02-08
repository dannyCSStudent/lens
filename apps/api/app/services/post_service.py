from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.enums import ContentStatus
from app.core.models.post import Post


async def get_posts(
    db: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
):
    stmt = (
        select(Post)
        .where(Post.status == "active")
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_post_by_id(db: AsyncSession, post_id: UUID):
    result = await db.execute(
        select(Post).where(
            Post.id == post_id,
            Post.status == ContentStatus.active,
        )
    )
    return result.scalar_one_or_none()