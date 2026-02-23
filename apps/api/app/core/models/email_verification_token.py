from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone, timedelta
import uuid


from app.core.models.base import Base


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash = mapped_column(String, nullable=False, unique=True)

    expires_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
)

    created_at = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
