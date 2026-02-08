"""expand moderation actions

Revision ID: a62c151e610f
Revises: 40058d7f4ec0
Create Date: 2026-02-07 18:02:41.874785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

moderation_target_type_enum = postgresql.ENUM(
    "post",
    "reply",
    "evidence",
    name="moderation_target_type",
)

moderation_action_enum = postgresql.ENUM(
    "removed_illegal",
    "locked",
    name="moderation_action",
)



# revision identifiers, used by Alembic.
revision: str = 'a62c151e610f'
down_revision: Union[str, Sequence[str], None] = '40058d7f4ec0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    moderation_target_type_enum.create(op.get_bind(), checkfirst=True)
    moderation_action_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "moderations",
        sa.Column("target_type", moderation_target_type_enum, nullable=False),
    )
    op.add_column(
        "moderations",
        sa.Column("target_id", sa.UUID(), nullable=False),
    )
    op.add_column(
        "moderations",
        sa.Column("action", moderation_action_enum, nullable=False),
    )
    op.add_column(
        "moderations",
        sa.Column("reason", sa.Text(), nullable=False),
    )
    op.add_column(
        "moderations",
        sa.Column("moderator_id", sa.UUID(), nullable=False),
    )
    op.add_column(
        "moderations",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "fk_moderations_moderator_id_users",
        "moderations",
        "users",
        ["moderator_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_index(
        "ix_moderations_target",
        "moderations",
        ["target_type", "target_id"],
    )



def downgrade() -> None:
    op.drop_index("ix_moderations_target", table_name="moderations")
    op.drop_constraint(
        "fk_moderations_moderator_id_users",
        "moderations",
        type_="foreignkey",
    )

    op.drop_column("moderations", "created_at")
    op.drop_column("moderations", "moderator_id")
    op.drop_column("moderations", "reason")
    op.drop_column("moderations", "action")
    op.drop_column("moderations", "target_id")
    op.drop_column("moderations", "target_type")

    moderation_action_enum.drop(op.get_bind(), checkfirst=True)
    moderation_target_type_enum.drop(op.get_bind(), checkfirst=True)

