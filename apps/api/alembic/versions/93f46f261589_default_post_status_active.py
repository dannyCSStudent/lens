"""default post status active

Revision ID: 93f46f261589
Revises: 794a43a170ba
Create Date: 2026-02-08 03:50:05.294449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93f46f261589'
down_revision: Union[str, Sequence[str], None] = '794a43a170ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "posts",
        "status",
        server_default=sa.text("'active'")
    )

def downgrade():
    op.alter_column(
        "posts",
        "status",
        server_default=None
    )