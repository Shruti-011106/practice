"""revenue_tracker_updates

Revision ID: c471b9a53e07
Revises: a8b9c0d1e2f3
Create Date: 2026-07-26 18:45:20.381410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c471b9a53e07'
down_revision: Union[str, Sequence[str], None] = 'a8b9c0d1e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op migration to preserve chain without destructive table drops
    pass


def downgrade() -> None:
    pass
