from sqlalchemy import (
    ForeignKey,
    Text,
    DateTime,
    func,
    Index,
    CheckConstraint,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID
import sqlalchemy as sa

from app.core.models.base import Base


class Reply(Base):
    __tablename__ = "replies"

    __table_args__ = (
        # Critical for reply velocity + post counts
        Index("idx_replies_post_created", "post_id", "created_at"),

        # ✅ DB-level protection
        CheckConstraint("like_count >= 0", name="replies_like_count_non_negative"),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("uuid_generate_v4()"),
    )

    post_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    author_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    parent_reply_id: Mapped[PyUUID | None] = mapped_column(
        ForeignKey("replies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)

    # -----------------------------
    # Engagement Counters
    # -----------------------------

    like_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=sa.text("0"),
    )

    status: Mapped[str] = mapped_column(
        sa.Enum("active", "removed_illegal", name="reply_status"),
        nullable=False,
        server_default=sa.text("'active'"),
    )

    created_at: Mapped[sa.DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
