"""merge all heads

Revision ID: f2b3c4d5e6f7
Revises: f1a2b3c4d5e6, 16f45ac1e3b2
Create Date: 2026-07-27 16:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = ('f1a2b3c4d5e6', '16f45ac1e3b2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
