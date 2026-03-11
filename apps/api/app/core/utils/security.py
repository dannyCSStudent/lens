# app/utils/security.py

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import SecurityEvent
from app.core.enums import SecurityEventType


async def log_security_event(
    db: AsyncSession,
    event_type: SecurityEventType,
    request: Request,
    user_id: str | None = None,
    metadata: dict | None = None,
):
    event = SecurityEvent(
        user_id=user_id,
        event_type=event_type.value,
        ip_address=request.headers.get(
            "x-forwarded-for",
            request.client.host
        ).split(",")[0].strip(),
        user_agent=request.headers.get("user-agent"),
        metadata=metadata,
    )

    db.add(event)
