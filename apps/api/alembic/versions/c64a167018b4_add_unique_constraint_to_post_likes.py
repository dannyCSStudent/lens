"""add unique constraint to post_likes

Revision ID: c64a167018b4
Revises: 212585fa7b75
Create Date: 2026-02-12 11:49:13.736270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c64a167018b4'
down_revision: Union[str, Sequence[str], None] = '212585fa7b75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_unique_constraint(
        "uq_post_like_user",
        "post_likes",
        ["post_id", "user_id"],
    )

def downgrade():
    op.drop_constraint(
        "uq_post_like_user",
        "post_likes",
        type_="unique",
    )

