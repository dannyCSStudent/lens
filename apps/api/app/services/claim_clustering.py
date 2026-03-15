import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.post import Post


def normalize_text(text: str):

    return text.lower().strip()


def generate_claim_fingerprint(text: str):

    normalized = normalize_text(text)

    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


async def cluster_claim(session: AsyncSession, post: Post):

    fingerprint = generate_claim_fingerprint(post.title or post.content)

    result = await session.execute(
        select(Post).where(Post.claim_cluster_id == fingerprint)
    )

    existing = result.scalars().first()

    if existing:

        post.claim_cluster_id = existing.claim_cluster_id
        post.claim_similarity_score = 1.0

    else:

        post.claim_cluster_id = fingerprint
        post.claim_similarity_score = 0.5

    await session.commit()
