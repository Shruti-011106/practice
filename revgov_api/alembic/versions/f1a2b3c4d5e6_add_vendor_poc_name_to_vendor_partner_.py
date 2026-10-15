"""Add vendor_poc_name to vendor_partner_hirings

Revision ID: f1a2b3c4d5e6
Revises: e8af4f1c4015
Create Date: 2026-07-27 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e8af4f1c4015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "vendor_partner_hirings",
        sa.Column("vendor_poc_name", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("vendor_partner_hirings", "vendor_poc_name")
