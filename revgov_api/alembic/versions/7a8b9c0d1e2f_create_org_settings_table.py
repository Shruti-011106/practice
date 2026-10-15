"""create org_settings table

Revision ID: 7a8b9c0d1e2f
Revises: 5537052089fc
Create Date: 2026-07-27 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a8b9c0d1e2f'
down_revision: Union[str, Sequence[str], None] = '5537052089fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'org_settings' not in inspector.get_table_names():
        op.create_table(
            'org_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('organization_name', sa.String(length=255), nullable=False),
            sa.Column('legal_name', sa.String(length=255), nullable=True),
            sa.Column('alias_name', sa.String(length=255), nullable=True),
            sa.Column('primary_domain', sa.String(length=255), nullable=True),
            sa.Column('industry', sa.String(length=100), nullable=True),
            sa.Column('company_size', sa.String(length=100), nullable=True),
            sa.Column('country', sa.String(length=100), nullable=True),
            sa.Column('company_logo', sa.String(length=500), nullable=True),
            sa.Column('admin_email', sa.String(length=255), nullable=False),
            sa.Column('support_email', sa.String(length=255), nullable=True),
            sa.Column('billing_contact_email', sa.String(length=255), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_org_settings_id'), 'org_settings', ['id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'org_settings' in inspector.get_table_names():
        op.drop_index(op.f('ix_org_settings_id'), table_name='org_settings')
        op.drop_table('org_settings')
