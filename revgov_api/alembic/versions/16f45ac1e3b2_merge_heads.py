"""merge_heads

Revision ID: 16f45ac1e3b2
Revises: 14149f5873c9, 7a8b9c0d1e2f
Create Date: 2026-07-27 16:11:17.561477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16f45ac1e3b2'
down_revision: Union[str, Sequence[str], None] = ('14149f5873c9', '7a8b9c0d1e2f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
