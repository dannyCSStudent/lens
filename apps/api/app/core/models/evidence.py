# models/evidence.py
from uuid import UUID
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    Text,
    DateTime,
    Index,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.models.base import Base


# --- ENUMS (model-level) ---
EvidenceTypeEnum = Enum(
    "link",
    "document",
    "image",
    "quote",
    name="evidence_type",
)

EvidenceDirectionEnum = Enum(
    "supports",
    "contradicts",
    name="evidence_direction",
)


class Evidence(Base):
    __tablename__ = "evidence"

    # --- Columns ---
    id: Mapped[UUID] = mapped_column(primary_key=True)

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )

    submitted_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    evidence_type: Mapped[str] = mapped_column(
        EvidenceTypeEnum,
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    upload_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_description: Mapped[str] = mapped_column(Text, nullable=False)

    direction: Mapped[str] = mapped_column(
        EvidenceDirectionEnum,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --- Indexes ---
    __table_args__ = (
        Index("ix_evidence_post_id", "post_id"),
        Index("ix_evidence_direction", "direction"),
    )
