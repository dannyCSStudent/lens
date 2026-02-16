from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func

from app.core.models.base import Base


class PostLike(Base):
    __tablename__ = "post_likes"

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_like_user"),
        # Critical for velocity queries
        Index("idx_post_likes_post_created", "post_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    post_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
