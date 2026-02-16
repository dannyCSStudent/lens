from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func

from app.core.models.base import Base


class ReplyLike(Base):
    __tablename__ = "reply_likes"

    __table_args__ = (
        UniqueConstraint("reply_id", "user_id", name="uq_reply_like_user"),
        Index("idx_reply_likes_reply_created", "reply_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    reply_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("replies.id", ondelete="CASCADE"),
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
