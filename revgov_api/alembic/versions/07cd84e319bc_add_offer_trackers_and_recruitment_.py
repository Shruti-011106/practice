"""add_offer_trackers_and_recruitment_fields

Revision ID: 07cd84e319bc
Revises: c0d1e2f3a4b5
Create Date: 2026-07-27 02:39:05.089095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '07cd84e319bc'
down_revision: Union[str, Sequence[str], None] = 'c0d1e2f3a4b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to job_openings
    op.add_column('job_openings', sa.Column('rounds_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('job_openings', sa.Column('interview_round_names', sa.String(), nullable=True))

    # Create offer_trackers table
    op.create_table('offer_trackers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('offer_id', sa.String(), nullable=True),
    sa.Column('candidate_id', sa.Integer(), nullable=True),
    sa.Column('candidate_name', sa.String(), nullable=False),
    sa.Column('offered_designation', sa.String(), nullable=False),
    sa.Column('offered_ctc', sa.String(), nullable=False),
    sa.Column('joining_date', sa.Date(), nullable=True),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('probation_period', sa.String(), nullable=True),
    sa.Column('remarks', sa.Text(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('offer_id')
    )
    op.create_index(op.f('ix_offer_trackers_id'), 'offer_trackers', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_offer_trackers_id'), table_name='offer_trackers')
    op.drop_table('offer_trackers')
    op.drop_column('job_openings', 'interview_round_names')
    op.drop_column('job_openings', 'rounds_count')
