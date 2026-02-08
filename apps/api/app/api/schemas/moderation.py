# app/api/schemas/moderation.py

from pydantic import BaseModel
from uuid import UUID
from typing import Literal, Optional

from app.core.enums import ContentStatus


class ModerateRequest(BaseModel):
    target_type: Literal["post", "reply"]
    target_id: UUID
    new_status: ContentStatus
    reason: Optional[str] = None
