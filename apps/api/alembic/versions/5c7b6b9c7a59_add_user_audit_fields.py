"""add user audit fields

Revision ID: 5c7b6b9c7a59
Revises: fe67cc6913cb
Create Date: 2026-03-22 14:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c7b6b9c7a59"
down_revision: Union[str, Sequence[str], None] = "fe67cc6913cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column("last_login_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")

    op.alter_column(
        "users",
        "is_moderator",
        server_default=sa.text("false"),
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "users",
        "is_admin",
        server_default=sa.text("false"),
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "users",
        "is_verified",
        server_default=sa.text("false"),
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "users",
        "failed_login_attempts",
        server_default=sa.text("0"),
        existing_type=sa.Integer(),
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "failed_login_attempts",
        server_default=None,
        existing_type=sa.Integer(),
    )
    op.alter_column(
        "users",
        "is_verified",
        server_default=None,
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "users",
        "is_admin",
        server_default=None,
        existing_type=sa.Boolean(),
    )
    op.alter_column(
        "users",
        "is_moderator",
        server_default=None,
        existing_type=sa.Boolean(),
    )
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "updated_at")
