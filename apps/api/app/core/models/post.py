import uuid
from sqlalchemy import Text, Enum, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.enums import ContentStatus
from app.core.models.base import Base
from sqlalchemy import Enum as SQLEnum

from app.core.enums import PostType, ContentStatus

class Post(Base):
    __tablename__ = "posts"

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

    post_type: Mapped[PostType] = mapped_column(Enum(PostType), index=True)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
    SQLEnum(ContentStatus, name="contentstatus"),
    nullable=False,
    server_default=text("'active'")
)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        index=True
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
