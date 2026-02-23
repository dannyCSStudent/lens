from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from app.core.models import SecurityEvent
from app.core.enums import SecurityEventType


async def get_security_summary(db: AsyncSession):
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    return {
        "total_events": await db.scalar(
            select(func.count()).where(SecurityEvent.created_at >= since)
        ),
        "failed_logins": await db.scalar(
            select(func.count()).where(
                SecurityEvent.event_type == SecurityEventType.login_failed.value,
                SecurityEvent.created_at >= since,
            )
        ),
        "accounts_locked": await db.scalar(
            select(func.count()).where(
                SecurityEvent.event_type == SecurityEventType.account_locked.value,
                SecurityEvent.created_at >= since,
            )
        ),
        "refresh_reuse_detected": await db.scalar(
            select(func.count()).where(
                SecurityEvent.event_type == SecurityEventType.refresh_reuse_detected.value,
                SecurityEvent.created_at >= since,
            )
        ),
    }


async def list_security_events(
    db: AsyncSession,
    limit: int,
    offset: int,
    event_type: str | None = None,
):
    query = select(SecurityEvent).order_by(SecurityEvent.created_at.desc())

    if event_type:
        query = query.where(SecurityEvent.event_type == event_type)

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def detect_bruteforce(db: AsyncSession):
    since = datetime.now(timezone.utc) - timedelta(hours=1)

    result = await db.execute(
        select(
            SecurityEvent.ip_address,
            func.count().label("attempts")
        )
        .where(
            SecurityEvent.event_type == SecurityEventType.login_failed.value,
            SecurityEvent.created_at >= since,
        )
        .group_by(SecurityEvent.ip_address)
        .having(func.count() >= 5)
    )

    return result.all()


