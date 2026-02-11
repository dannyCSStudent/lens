# app/api/schemas/moderation.py

from pydantic import BaseModel
from uuid import UUID
from typing import Literal, Optional
from datetime import datetime
from app.core.enums import ContentStatus


class ModerateRequest(BaseModel):
    target_type: Literal["post", "reply"]
    target_id: UUID
    new_status: ContentStatus
    reason: Optional[str] = None



ModerationTargetType = Literal["post", "reply", "evidence"]
ModerationActionType = Literal["removed_illegal", "locked"]


class ModerationActionRead(BaseModel):
    id: UUID
    moderator_id: UUID
    target_type: ModerationTargetType
    target_id: UUID
    action: ModerationActionType
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ModerationHistoryQueryParams(BaseModel):
    moderator_id: Optional[UUID] = None
    target_type: Optional[ModerationTargetType] = None
    target_id: Optional[UUID] = None
    status: Optional[ModerationActionType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    offset: int = 0