"""update_reusable_assets_fields

Revision ID: bb28548b524a
Revises: a7a69b3fa7b9
Create Date: 2026-07-08 14:57:13.704998

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bb28548b524a"
down_revision: Union[str, Sequence[str], None] = "e2a34567890b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to reusable_assets
    op.add_column(
        "reusable_assets", sa.Column("document_type", sa.String(), nullable=True)
    )
    op.add_column(
        "reusable_assets", sa.Column("document_url", sa.String(), nullable=True)
    )
    op.add_column(
        "reusable_assets", sa.Column("document_name", sa.String(), nullable=True)
    )
    op.add_column(
        "reusable_assets", sa.Column("approval_status", sa.String(), nullable=True)
    )
    op.add_column(
        "reusable_assets", sa.Column("last_review_date", sa.Date(), nullable=True)
    )
    op.add_column("reusable_assets", sa.Column("tag", sa.String(), nullable=True))

    # Drop columns from reusable_assets
    op.drop_column("reusable_assets", "reuse_count")


def downgrade() -> None:
    # Add back dropped columns
    op.add_column(
        "reusable_assets",
        sa.Column("reuse_count", sa.Integer(), server_default="0", nullable=True),
    )

    # Drop added columns
    op.drop_column("reusable_assets", "tag")
    op.drop_column("reusable_assets", "last_review_date")
    op.drop_column("reusable_assets", "approval_status")
    op.drop_column("reusable_assets", "document_name")
    op.drop_column("reusable_assets", "document_url")
    op.drop_column("reusable_assets", "document_type")
