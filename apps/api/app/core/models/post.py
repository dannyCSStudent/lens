import uuid
from sqlalchemy import (
    Text,
    ForeignKey,
    TIMESTAMP,
    text,
    Index,
    CheckConstraint,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum

from app.core.enums import PostType, ContentStatus
from app.core.models.base import Base


class Post(Base):
    __tablename__ = "posts"

    __table_args__ = (
        # Composite index for feed queries
        Index("idx_posts_status_created_at", "status", "created_at", "id"),
        Index("idx_posts_like_count", "like_count"),

        # ✅ DB-level protection
        CheckConstraint("like_count >= 0", name="posts_like_count_non_negative"),
        CheckConstraint("reply_count >= 0", name="posts_reply_count_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True
    )

    post_type: Mapped[PostType] = mapped_column(
        SQLEnum(PostType),
        index=True
    )

    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)

    # -----------------------------
    # Engagement Counters
    # -----------------------------

    like_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    reply_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    status: Mapped[ContentStatus] = mapped_column(
        SQLEnum(ContentStatus, name="contentstatus"),
        nullable=False,
        server_default=text("'active'")
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
