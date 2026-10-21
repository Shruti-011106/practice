"""merge multiple heads

Revision ID: e3f4g5h6i7j8
Revises: c3d4e5f6a7b8, da5442beffc2
Create Date: 2026-07-09 20:00:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "e3f4g5h6i7j8"
down_revision: Union[str, Sequence[str], None] = ("c3d4e5f6a7b8", "bab10ba5bd76")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
