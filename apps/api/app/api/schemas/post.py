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
from typing import Optional

class PostRead(PostBase):
    id: UUID
    author_id: UUID
    status: PostStatus
    created_at: datetime
    updated_at: datetime

    like_count: Optional[int] = 0
    reply_count: Optional[int] = 0
    liked_by_current_user: Optional[bool] = False

    class Config:
        from_attributes = True

