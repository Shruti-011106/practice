"""truncate vendor partner hirings

Revision ID: e2a34567890b
Revises: da5442beffc2
Create Date: 2026-07-08 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e2a34567890b"
down_revision: Union[str, Sequence[str], None] = "da5442beffc2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Truncate the table to remove existing null rows that break the new schema
    op.execute("TRUNCATE TABLE vendor_partner_hirings RESTART IDENTITY CASCADE;")


def downgrade() -> None:
    # No way to restore truncated data
    pass
