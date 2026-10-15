"""update_budget_tracker_to_project

Revision ID: a8b9c0d1e2f3
Revises: 1262e2fc0381
Create Date: 2026-07-26 18:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, Sequence[str], None] = '1262e2fc0381'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old columns and FK
    try:
        op.drop_constraint('budget_trackers_department_id_fkey', 'budget_trackers', type_='foreignkey')
    except Exception:
        pass
    
    op.drop_column('budget_trackers', 'department_id')
    op.drop_column('budget_trackers', 'financial_year')
    op.drop_column('budget_trackers', 'quarter')
    op.drop_column('budget_trackers', 'budget_allocated')
    op.drop_column('budget_trackers', 'budget_utilized')
    op.drop_column('budget_trackers', 'remaining_budget')

    # Add new project-based budget columns
    op.add_column('budget_trackers', sa.Column('project_id', sa.Integer(), nullable=True))
    op.add_column('budget_trackers', sa.Column('budget', sa.Float(), server_default='0', nullable=True))
    op.add_column('budget_trackers', sa.Column('consumed', sa.Float(), server_default='0', nullable=True))
    op.add_column('budget_trackers', sa.Column('remaining', sa.Float(), server_default='0', nullable=True))
    op.add_column('budget_trackers', sa.Column('forecast', sa.Float(), server_default='0', nullable=True))
    op.add_column('budget_trackers', sa.Column('variance', sa.Float(), server_default='0', nullable=True))
    
    op.create_foreign_key('budget_trackers_project_id_fkey', 'budget_trackers', 'project_governances', ['project_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('budget_trackers_project_id_fkey', 'budget_trackers', type_='foreignkey')
    
    op.drop_column('budget_trackers', 'variance')
    op.drop_column('budget_trackers', 'forecast')
    op.drop_column('budget_trackers', 'remaining')
    op.drop_column('budget_trackers', 'consumed')
    op.drop_column('budget_trackers', 'budget')
    op.drop_column('budget_trackers', 'project_id')

    op.add_column('budget_trackers', sa.Column('remaining_budget', sa.Float(), server_default='0', nullable=True))
    op.add_column('budget_trackers', sa.Column('budget_utilized', sa.Float(), server_default='0', nullable=True))
    op.add_column('budget_trackers', sa.Column('budget_allocated', sa.Float(), server_default='0', nullable=True))
    op.add_column('budget_trackers', sa.Column('quarter', sa.String(), nullable=True))
    op.add_column('budget_trackers', sa.Column('financial_year', sa.String(), nullable=True))
    op.add_column('budget_trackers', sa.Column('department_id', sa.Integer(), nullable=True))
    
    op.create_foreign_key('budget_trackers_department_id_fkey', 'budget_trackers', 'department_masters', ['department_id'], ['id'])
