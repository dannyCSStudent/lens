from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import mapped_column
from app.core.models.base import Base



class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    event_type = mapped_column(String, nullable=False)

    ip_address = mapped_column(String, nullable=True)
    user_agent = mapped_column(String, nullable=True)

    event_metadata = mapped_column(
        "metadata",  # keeps DB column named metadata
        JSON,
        nullable=True,
    )

    created_at = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

