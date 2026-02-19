"""add non-negative counter constraints

Revision ID: 960a41207de4
Revises: 02d01809b471
Create Date: 2026-02-18 17:39:03.280865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '960a41207de4'
down_revision: Union[str, Sequence[str], None] = '02d01809b471'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        ALTER TABLE posts
        ADD CONSTRAINT posts_like_count_non_negative
        CHECK (like_count >= 0);
        """
    )

    op.execute(
        """
        ALTER TABLE posts
        ADD CONSTRAINT posts_reply_count_non_negative
        CHECK (reply_count >= 0);
        """
    )

    op.execute(
        """
        ALTER TABLE replies
        ADD CONSTRAINT replies_like_count_non_negative
        CHECK (like_count >= 0);
        """
    )


def downgrade():
    op.execute(
        "ALTER TABLE posts DROP CONSTRAINT posts_like_count_non_negative;"
    )

    op.execute(
        "ALTER TABLE posts DROP CONSTRAINT posts_reply_count_non_negative;"
    )

    op.execute(
        "ALTER TABLE replies DROP CONSTRAINT replies_like_count_non_negative;"
    )