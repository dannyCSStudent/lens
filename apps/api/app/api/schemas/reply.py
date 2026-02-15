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
    parent_reply_id: Optional[UUID] = None
    author_id: UUID
    body: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    like_count: int 

    # children are optional, only populated when requested
    children: Optional[List["ReplyRead"]] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        # Enables recursive models
        arbitrary_types_allowed = True


# Needed for recursive Pydantic models
ReplyRead.model_rebuild()


class ReplyTreeRead(ReplyRead):
    children: list["ReplyTreeRead"] = []

ReplyTreeRead.model_rebuild()
