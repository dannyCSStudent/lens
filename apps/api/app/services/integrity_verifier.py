from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.models.evidence import Evidence
from app.services.archive_service import fetch_page_content, generate_content_hash
from app.services.credibility_engine import calculate_credibility_score


async def verify_evidence_integrity(session: AsyncSession):

    result = await session.execute(
        select(Evidence).where(Evidence.source_url.is_not(None))
    )

    evidence_list = result.scalars().all()

    for evidence in evidence_list:

        try:
            # Fetch current source content
            content = await fetch_page_content(str(evidence.source_url))

            # Generate new fingerprint
            new_hash = generate_content_hash(content)

            # Detect tampering
            if evidence.content_hash and evidence.content_hash != new_hash:
                evidence.tampered = True
            else:
                evidence.tampered = False

            # Update verification timestamp
            evidence.last_verified_at = datetime.utcnow()

            # Recalculate credibility score
            evidence.credibility_score = calculate_credibility_score(
                evidence.weight,
                None,  # source reputation can be added later
                evidence.tampered,
            )

        except Exception:
            # Network failures or dead links should not crash verification
            continue

    await session.commit()
