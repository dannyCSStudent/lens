from datetime import datetime
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, Field


class ReplyCreate(BaseModel):
    post_id: UUID
    body: str = Field(..., min_length=1)
    parent_reply_id: Optional[UUID] = None


class ReplyRead(BaseModel):
    id: UUID
    post_id: UUID
    parent_reply_id: Optional[UUID]
    author_id: UUID
    body: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReplyTreeRead(ReplyRead):
    children: list["ReplyTreeRead"] = []

ReplyTreeRead.model_rebuild()
