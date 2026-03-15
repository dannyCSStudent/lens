from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.evidence import Evidence
from app.core.models.post import Post


async def update_post_truth(session: AsyncSession, post_id):

    result = await session.execute(
        select(Evidence).where(Evidence.post_id == post_id)
    )

    evidence_list = result.scalars().all()

    if not evidence_list:
        return

    support = 0
    contradict = 0

    for e in evidence_list:

        score = e.credibility_score or 0.3

        if e.direction == "supports":
            support += score
        else:
            contradict += score

    raw_score = support - contradict

    normalized = max(0.0, min((raw_score + 1) / 2, 1))

    confidence = min(len(evidence_list) / 5, 1)

    post = await session.get(Post, post_id)

    if post:
        post.truth_score = normalized
        post.truth_confidence = confidence

        await session.commit()
