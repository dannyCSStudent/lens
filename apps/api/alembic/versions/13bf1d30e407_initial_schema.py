"""initial schema

Revision ID: 13bf1d30e407
Revises:
Create Date: 2026-01-31 13:00:57.488717
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "13bf1d30e407"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


# ENUM definitions (NO execution here)
user_status_enum = postgresql.ENUM(
    "ACTIVE",
    "SUSPENDED",
    name="user_status",
    create_type=False,
)


post_type_enum = postgresql.ENUM(
    "expression",
    "claim",
    "investigation",
    name="posttype",
    create_type=False,
)

content_status_enum = postgresql.ENUM(
    "active",
    "locked",
    "removed_illegal",
    name="contentstatus",
    create_type=False,
)


def upgrade() -> None:
    # Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ENUM types (safe + idempotent)
    user_status_enum.create(op.get_bind(), checkfirst=True)
    post_type_enum.create(op.get_bind(), checkfirst=True)
    content_status_enum.create(op.get_bind(), checkfirst=True)

    # USERS
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "is_moderator",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "status",
            user_status_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # POSTS
    op.create_table(
        "posts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_type", post_type_enum, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", content_status_enum, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_posts_author_id", "posts", ["author_id"])
    op.create_index("ix_posts_created_at", "posts", ["created_at"])
    op.create_index("ix_posts_post_type", "posts", ["post_type"])

    # CHILD TABLES
    for table in [
        "evidence",
        "moderations",
        "notifications",
        "replies",
        "reports",
    ]:
        op.create_table(
            table,
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                server_default=sa.text("uuid_generate_v4()"),
                nullable=False,
            ),
            sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    for table in [
        "reports",
        "replies",
        "notifications",
        "moderations",
        "evidence",
    ]:
        op.drop_table(table)

    op.drop_index("ix_posts_post_type", table_name="posts")
    op.drop_index("ix_posts_created_at", table_name="posts")
    op.drop_index("ix_posts_author_id", table_name="posts")
    op.drop_table("posts")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # ENUM cleanup (reverse order!)
    content_status_enum.drop(op.get_bind(), checkfirst=True)
    post_type_enum.drop(op.get_bind(), checkfirst=True)
    user_status_enum.drop(op.get_bind(), checkfirst=True)
