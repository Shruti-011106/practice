"""add_request_order_trackers

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
Create Date: 2026-07-26 19:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9c0d1e2f3a4'
down_revision: Union[str, Sequence[str], None] = 'c471b9a53e07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'request_order_trackers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('item', sa.String(), nullable=True),
        sa.Column('cost', sa.Float(), server_default='0', nullable=True),
        sa.Column('approval_status', sa.String(), server_default='Pending Approval', nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['department_masters.id'], name='request_order_trackers_department_id_fkey'),
        sa.ForeignKeyConstraint(['project_id'], ['project_governances.id'], name='request_order_trackers_project_id_fkey'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_partner_hirings.id'], name='request_order_trackers_vendor_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_request_order_trackers_id'), 'request_order_trackers', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_request_order_trackers_id'), table_name='request_order_trackers')
    op.drop_table('request_order_trackers')
