from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.enums import PostType, ContentStatus
from typing import Optional


class UserPublic(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None


class PostCard(BaseModel):
    id: UUID
    post_type: PostType
    title: str
    author: UserPublic
    created_at: datetime
    evidence_count: int
    confidence_state: str
    status: ContentStatus
    trending_score: float

