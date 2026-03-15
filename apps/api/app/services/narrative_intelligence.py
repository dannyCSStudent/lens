import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.evidence import Evidence
from app.core.models.post import Post


def generate_cluster_id(source_ids):

    sorted_ids = sorted(source_ids)

    raw = "|".join(str(s) for s in sorted_ids)

    return hashlib.sha256(raw.encode()).hexdigest()[:16]


async def analyze_post_narrative(session: AsyncSession, post_id):

    result = await session.execute(
        select(Evidence).where(Evidence.post_id == post_id)
    )

    evidence_list = result.scalars().all()

    source_ids = set()

    for e in evidence_list:
        if e.source_id:
            source_ids.add(e.source_id)

    if not source_ids:
        return

    cluster_id = generate_cluster_id(source_ids)

    # Count posts sharing these sources
    result = await session.execute(
        select(Evidence.post_id).where(Evidence.source_id.in_(source_ids))
    )

    related_posts = {row[0] for row in result}

    cluster_size = len(related_posts)

    risk_score = min(cluster_size / 10, 1.0)

    post = await session.get(Post, post_id)

    if post:

        post.narrative_cluster_id = cluster_id
        post.narrative_risk_score = risk_score

        await session.commit()
