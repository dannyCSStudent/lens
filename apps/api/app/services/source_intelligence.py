from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.models.source import Source
from app.core.models.evidence import Evidence


async def update_source_reputation(session: AsyncSession, source_id):

    result = await session.execute(
        select(Evidence).where(Evidence.source_id == source_id)
    )

    evidence_list = result.scalars().all()

    if not evidence_list:
        return

    total = len(evidence_list)

    credibility_sum = 0
    tamper_count = 0

    for e in evidence_list:

        credibility_sum += e.credibility_score or 0.3

        if getattr(e, "tampered", False):
            tamper_count += 1

    reputation = credibility_sum / total

    source = await session.get(Source, source_id)

    if source:

        source.reputation_score = reputation
        source.tamper_events = tamper_count
        source.citation_count = total
        source.last_evaluated_at = datetime.utcnow()

        await session.commit()
