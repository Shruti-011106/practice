"""procurement_payment_revenue_flow

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
Create Date: 2026-07-26 20:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0d1e2f3a4b5'
down_revision: Union[str, Sequence[str], None] = 'b9c0d1e2f3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns to po_trackers
    op.add_column('po_trackers', sa.Column('request_order_id', sa.Integer(), nullable=True))
    op.add_column('po_trackers', sa.Column('delivery_date', sa.Date(), nullable=True))
    op.create_foreign_key('po_trackers_request_order_id_fkey', 'po_trackers', 'request_order_trackers', ['request_order_id'], ['id'])

    # 2. Add columns to invoice_trackers
    op.add_column('invoice_trackers', sa.Column('po_id', sa.Integer(), nullable=True))
    op.add_column('invoice_trackers', sa.Column('tax', sa.Float(), server_default='0', nullable=True))
    op.create_foreign_key('invoice_trackers_po_id_fkey', 'invoice_trackers', 'po_trackers', ['po_id'], ['id'])

    # 3. Create payment_trackers table
    op.create_table(
        'payment_trackers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.String(), nullable=True),
        sa.Column('invoice_id', sa.Integer(), nullable=True),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), server_default='0', nullable=True),
        sa.Column('method', sa.String(), server_default='Bank Transfer', nullable=True),
        sa.Column('reference', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='Pending', nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice_trackers.id'], name='payment_trackers_invoice_id_fkey'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_partner_hirings.id'], name='payment_trackers_vendor_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_trackers_id'), 'payment_trackers', ['id'], unique=False)
    op.create_index(op.f('ix_payment_trackers_payment_id'), 'payment_trackers', ['payment_id'], unique=True)

    # 4. Recreate revenue_trackers table with new simplified schema
    op.execute('DROP TABLE IF EXISTS revenue_trackers CASCADE')
    op.create_table(
        'revenue_trackers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('revenue_id', sa.String(), nullable=True),
        sa.Column('month', sa.String(), nullable=True),
        sa.Column('sales_owner_id', sa.Integer(), nullable=True),
        sa.Column('payment_id', sa.Integer(), nullable=True),
        sa.Column('target_revenue', sa.Float(), server_default='0', nullable=True),
        sa.Column('achieved_revenue', sa.Float(), server_default='0', nullable=True),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='Open', nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['sales_owner_id'], ['employees.id'], name='revenue_trackers_sales_owner_id_fkey'),
        sa.ForeignKeyConstraint(['payment_id'], ['payment_trackers.id'], name='revenue_trackers_payment_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_revenue_trackers_id'), 'revenue_trackers', ['id'], unique=False)
    op.create_index(op.f('ix_revenue_trackers_revenue_id'), 'revenue_trackers', ['revenue_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_revenue_trackers_revenue_id'), table_name='revenue_trackers')
    op.drop_index(op.f('ix_revenue_trackers_id'), table_name='revenue_trackers')
    op.drop_table('revenue_trackers')

    op.drop_index(op.f('ix_payment_trackers_payment_id'), table_name='payment_trackers')
    op.drop_index(op.f('ix_payment_trackers_id'), table_name='payment_trackers')
    op.drop_table('payment_trackers')

    op.drop_constraint('invoice_trackers_po_id_fkey', 'invoice_trackers', type_='foreignkey')
    op.drop_column('invoice_trackers', 'tax')
    op.drop_column('invoice_trackers', 'po_id')

    op.drop_constraint('po_trackers_request_order_id_fkey', 'po_trackers', type_='foreignkey')
    op.drop_column('po_trackers', 'delivery_date')
    op.drop_column('po_trackers', 'request_order_id')
