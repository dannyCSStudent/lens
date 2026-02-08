# models/moderation.py
from sqlalchemy import Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa
from uuid import UUID as PyUUID

from app.core.models.base import Base


class ModerationAction(Base):
    __tablename__ = "moderations"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("uuid_generate_v4()"),
    )

    target_type: Mapped[str] = mapped_column(
        sa.Enum("post", "reply", "evidence", name="moderation_target_type"),
        nullable=False,
    )

    target_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        sa.Enum("removed_illegal", "locked", name="moderation_action"),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(Text, nullable=False)

    moderator_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    created_at: Mapped[sa.DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
