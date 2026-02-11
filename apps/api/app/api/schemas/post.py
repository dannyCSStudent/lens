from datetime import datetime
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, Field


# ---- Enums ----
PostType = Literal["expression", "claim", "investigation"]
PostStatus = Literal["active", "locked", "removed_illegal"]


# ---- Base ----
class PostBase(BaseModel):
    title: str
    body: str
    post_type: PostType


# ---- Create ----
class PostCreate(PostBase):
    pass


# ---- Read ----
class PostRead(PostBase):
    id: UUID
    author_id: UUID
    status: PostStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
