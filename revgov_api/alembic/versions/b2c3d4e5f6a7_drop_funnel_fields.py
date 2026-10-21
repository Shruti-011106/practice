"""drop funnel fields from job_openings

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-09 18:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop funnel tracking columns from job_openings
    op.drop_column("job_openings", "applications_received")
    op.drop_column("job_openings", "shortlisted")
    op.drop_column("job_openings", "interviewed")
    op.drop_column("job_openings", "offered")
    op.drop_column("job_openings", "joined")
    op.drop_column("job_openings", "offer_drop")


def downgrade() -> None:
    # Add columns back if we need to rollback
    op.add_column(
        "job_openings",
        sa.Column(
            "applications_received", sa.Integer(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "job_openings",
        sa.Column("shortlisted", sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "job_openings",
        sa.Column("interviewed", sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "job_openings",
        sa.Column("offered", sa.Integer(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "job_openings",
        sa.Column("joined", sa.Integer(), autoincrement=False, nullable=True),
    )

    # We recreate the enum if it was used for offer_drop, assuming it exists
    offerdrop_enum = postgresql.ENUM("ACCEPTED", "DROP", name="offerdropenum")
    op.add_column(
        "job_openings",
        sa.Column("offer_drop", offerdrop_enum, autoincrement=False, nullable=True),
    )
