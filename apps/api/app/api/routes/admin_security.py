from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth.admin import require_admin
from app.services.security_service import (
    get_security_summary,
    list_security_events,
    detect_bruteforce,
)
from app.api.schemas.admin_security import (
    SecuritySummaryResponse,
    SecurityEventResponse,
    SuspiciousIPResponse,
)

router = APIRouter(prefix="/admin/security", tags=["admin-security"])


@router.get("/summary", response_model=SecuritySummaryResponse)
async def security_summary(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    return await get_security_summary(db)


@router.get("/events", response_model=list[SecurityEventResponse])
async def list_events(
    limit: int = Query(50, le=200),
    offset: int = 0,
    event_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    events = await list_security_events(db, limit, offset, event_type)

    return [
        {
            "id": str(e.id),
            "user_id": str(e.user_id) if e.user_id else None,
            "event_type": e.event_type,
            "ip_address": e.ip_address,
            "user_agent": e.user_agent,
            "metadata": e.event_metadata,
            "created_at": e.created_at,
        }
        for e in events
    ]


@router.get("/suspicious/brute-force", response_model=list[SuspiciousIPResponse])
async def suspicious_ips(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    rows = await detect_bruteforce(db)

    return [
        {
            "ip_address": row.ip_address,
            "failed_attempts_last_hour": row.attempts,
        }
        for row in rows
    ]


