from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.core.models.evidence import Evidence
from app.core.models.source import Source
from app.services.truth_engine import update_post_truth
from app.api.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.services.evidence_weight import calculate_evidence_weight
from app.services.archive_service import fetch_page_content, generate_content_hash


router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/", response_model=EvidenceResponse)
async def create_evidence(
    payload: EvidenceCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Add evidence supporting or contradicting a claim (post).
    """

    source_id = None
    source_reputation = None
    archive_url = None
    content_hash = None

    # --------------------------------
    # SOURCE HANDLING
    # --------------------------------

    if payload.source_url:
        domain = payload.source_url.host

        result = await session.execute(
            select(Source).where(Source.domain == domain)
        )

        source = result.scalar_one_or_none()

        if not source:
            source = Source(
                domain=domain,
                reputation_score=0.5,
            )
            session.add(source)
            await session.flush()

        source_id = source.id
        source_reputation = source.reputation_score

    # --------------------------------
    # EVIDENCE WEIGHT ENGINE
    # --------------------------------

    weight = calculate_evidence_weight(
        payload.evidence_type,
        source_reputation,
    )

    # --------------------------------
    # ARCHIVE + CONTENT HASH
    # --------------------------------

    if payload.source_url:
        try:
            page_content = await fetch_page_content(str(payload.source_url))
            content_hash = generate_content_hash(page_content)

            # archive.org snapshot link
            archive_url = f"https://web.archive.org/save/{payload.source_url}"

        except Exception:
            # archiving failure should NOT block evidence submission
            content_hash = None
            archive_url = None

    # --------------------------------
    # CREATE EVIDENCE RECORD
    # --------------------------------

    evidence = Evidence(
        post_id=payload.post_id,
        evidence_type=payload.evidence_type,
        direction=payload.direction,
        source_description=payload.source_description,
        source_url=str(payload.source_url) if payload.source_url else None,
        upload_path=payload.upload_path,
        source_id=source_id,
        weight=weight,
        archive_url=archive_url,
        content_hash=content_hash,
    )

    session.add(evidence)
    await session.commit()
    await session.refresh(evidence)

    # --------------------------------
    # RECALCULATE TRUTH SCORE
    # --------------------------------

    await update_post_truth(session, payload.post_id)

    return evidence


@router.get("/post/{post_id}", response_model=list[EvidenceResponse])
async def get_post_evidence(
    post_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """
    Get all evidence attached to a post.
    """

    result = await session.execute(
        select(Evidence).where(Evidence.post_id == post_id)
    )

    return result.scalars().all()
