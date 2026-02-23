from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SecuritySummaryResponse(BaseModel):
    total_events: int
    failed_logins: int
    accounts_locked: int
    refresh_reuse_detected: int


class SecurityEventResponse(BaseModel):
    id: str
    user_id: Optional[str]
    event_type: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Optional[dict]
    created_at: datetime


class SuspiciousIPResponse(BaseModel):
    ip_address: str
    failed_attempts_last_hour: int
