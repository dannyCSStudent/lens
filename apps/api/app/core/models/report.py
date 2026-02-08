# models/report.py
from sqlalchemy import Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa
from uuid import UUID as PyUUID

from app.core.models.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("uuid_generate_v4()"),
    )

    reporter_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    target_type: Mapped[str] = mapped_column(
        sa.Enum("post", "reply", "evidence", name="report_target_type"),
        nullable=False,
    )

    target_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(Text, nullable=False)

    resolved: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sa.text("false"),
        nullable=False,
    )

    created_at: Mapped[sa.DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
