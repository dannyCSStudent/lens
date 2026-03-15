from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.evidence import Evidence
from app.core.models.post import Post


async def analyze_post_network(session: AsyncSession, post_id):

    result = await session.execute(
        select(Evidence).where(Evidence.post_id == post_id)
    )

    evidence_list = result.scalars().all()

    sources = set()
    supporting = 0
    contradicting = 0

    for e in evidence_list:

        if e.source_id:
            sources.add(e.source_id)

        if e.direction == "supports":
            supporting += 1
        else:
            contradicting += 1

    return {
        "unique_sources": len(sources),
        "supporting_evidence": supporting,
        "contradicting_evidence": contradicting,
        "evidence_count": len(evidence_list),
    }


def detect_single_source_narrative(metrics):

    if metrics["unique_sources"] <= 1 and metrics["evidence_count"] >= 3:
        return True

    return False

def detect_confirmation_cluster(metrics):

    if metrics["supporting_evidence"] >= 4 and metrics["contradicting_evidence"] == 0:
        return True

    return False
