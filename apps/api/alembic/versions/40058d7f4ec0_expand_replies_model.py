"""expand replies model

Revision ID: 40058d7f4ec0
Revises: 55e0818601db
Create Date: 2026-02-07 17:57:46.983931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

reply_status_enum = postgresql.ENUM(
    "active",
    "removed_illegal",
    name="reply_status",
)



# revision identifiers, used by Alembic.
revision: str = '40058d7f4ec0'
down_revision: Union[str, Sequence[str], None] = '55e0818601db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    reply_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "replies",
        sa.Column("author_id", sa.UUID(), nullable=False),
    )
    op.add_column(
        "replies",
        sa.Column("parent_reply_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "replies",
        sa.Column("status", reply_status_enum, nullable=False, server_default="active"),
    )
    op.add_column(
        "replies",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("ix_replies_post_id", "replies", ["post_id"])
    op.create_index("ix_replies_parent_reply_id", "replies", ["parent_reply_id"])

    op.create_foreign_key(
        "fk_replies_author_id_users",
        "replies",
        "users",
        ["author_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_replies_parent_reply_id_replies",
        "replies",
        "replies",
        ["parent_reply_id"],
        ["id"],
        ondelete="CASCADE",
    )



def downgrade() -> None:
    op.drop_constraint("fk_replies_parent_reply_id_replies", "replies", type_="foreignkey")
    op.drop_constraint("fk_replies_author_id_users", "replies", type_="foreignkey")

    op.drop_index("ix_replies_parent_reply_id", table_name="replies")
    op.drop_index("ix_replies_post_id", table_name="replies")

    op.drop_column("replies", "created_at")
    op.drop_column("replies", "status")
    op.drop_column("replies", "parent_reply_id")
    op.drop_column("replies", "author_id")

    reply_status_enum.drop(op.get_bind(), checkfirst=True)

