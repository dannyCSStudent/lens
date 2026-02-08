"""expand reports model

Revision ID: 44c7ae592dba
Revises: a62c151e610f
Create Date: 2026-02-07 18:05:23.296598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

report_target_type_enum = postgresql.ENUM(
    "post",
    "reply",
    "evidence",
    name="report_target_type",
)



# revision identifiers, used by Alembic.
revision: str = '44c7ae592dba'
down_revision: Union[str, Sequence[str], None] = 'a62c151e610f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    report_target_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "reports",
        sa.Column("reporter_id", sa.UUID(), nullable=False),
    )
    op.add_column(
        "reports",
        sa.Column("target_type", report_target_type_enum, nullable=False),
    )
    op.add_column(
        "reports",
        sa.Column("target_id", sa.UUID(), nullable=False),
    )
    op.add_column(
        "reports",
        sa.Column("reason", sa.Text(), nullable=False),
    )
    op.add_column(
        "reports",
        sa.Column(
            "resolved",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column(
        "reports",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "fk_reports_reporter_id_users",
        "reports",
        "users",
        ["reporter_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_index(
        "ix_reports_target",
        "reports",
        ["target_type", "target_id"],
    )



def downgrade() -> None:
    op.drop_index("ix_reports_target", table_name="reports")

    op.drop_constraint(
        "fk_reports_reporter_id_users",
        "reports",
        type_="foreignkey",
    )

    op.drop_column("reports", "created_at")
    op.drop_column("reports", "resolved")
    op.drop_column("reports", "reason")
    op.drop_column("reports", "target_id")
    op.drop_column("reports", "target_type")
    op.drop_column("reports", "reporter_id")

    report_target_type_enum.drop(op.get_bind(), checkfirst=True)

