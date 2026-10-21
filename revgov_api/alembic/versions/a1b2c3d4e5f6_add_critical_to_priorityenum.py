"""add critical to priorityenum

Revision ID: a1b2c3d4e5f6
Revises: 4716af839abd
Create Date: 2026-07-09 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "4716af839abd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL requires that ALTER TYPE ... ADD VALUE is executed outside a transaction block.
    # By issuing a COMMIT first, we close the current transaction block.
    op.execute("COMMIT")
    op.execute("ALTER TYPE priorityenum ADD VALUE IF NOT EXISTS 'CRITICAL'")


def downgrade() -> None:
    # Removing a value from a PostgreSQL enum is not supported directly,
    # so we leave downgrade empty.
    pass
