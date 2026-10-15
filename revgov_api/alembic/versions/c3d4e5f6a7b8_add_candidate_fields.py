"""add missing candidate fields

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-09 18:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the missing columns to the candidates table
    op.add_column("candidates", sa.Column("notice_period", sa.String(), nullable=True))
    op.add_column("candidates", sa.Column("current_ctc", sa.String(), nullable=True))
    op.add_column("candidates", sa.Column("remarks_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    # Drop the columns if we rollback
    op.drop_column("candidates", "remarks_notes")
    op.drop_column("candidates", "current_ctc")
    op.drop_column("candidates", "notice_period")
