"""update_payments_for_monthly_billing

Revision ID: abc789def012
Revises: def456789abc
Create Date: 2026-06-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'abc789def012'
down_revision: Union[str, Sequence[str], None] = 'def456789abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('PAYMENTS', sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('USERS.user_id', ondelete='SET NULL'), nullable=True))
    op.add_column('PAYMENTS', sa.Column('period_start', sa.Date(), nullable=False, server_default=sa.text('(CURDATE())')))
    op.add_column('PAYMENTS', sa.Column('period_end', sa.Date(), nullable=False, server_default=sa.text('(CURDATE())')))
    op.add_column('PAYMENTS', sa.Column('due_date', sa.Date(), nullable=False, server_default=sa.text('(CURDATE())')))
    op.add_column('PAYMENTS', sa.Column('submitted_at', sa.DateTime(), nullable=True))
    op.add_column('PAYMENTS', sa.Column('verified_by', sa.Integer(), sa.ForeignKey('USERS.user_id', ondelete='SET NULL'), nullable=True))
    op.add_column('PAYMENTS', sa.Column('notes', sa.Text(), nullable=True))

    op.alter_column('PAYMENTS', 'method',
        existing_type=sa.Enum('gcash', 'bank_transfer', 'cash', 'card'),
        type_=sa.Enum('gcash', 'bank_transfer', 'cash'),
        existing_nullable=False,
        nullable=True)
    op.alter_column('PAYMENTS', 'status',
        existing_type=sa.Enum('pending', 'completed', 'failed', 'refunded'),
        type_=sa.Enum('pending', 'paid', 'completed', 'failed', 'refunded'),
        existing_nullable=False,
        existing_server_default='pending')


def downgrade() -> None:
    op.drop_column('PAYMENTS', 'notes')
    op.drop_column('PAYMENTS', 'verified_by')
    op.drop_column('PAYMENTS', 'submitted_at')
    op.drop_column('PAYMENTS', 'due_date')
    op.drop_column('PAYMENTS', 'period_end')
    op.drop_column('PAYMENTS', 'period_start')
    op.drop_column('PAYMENTS', 'tenant_id')
    op.alter_column('PAYMENTS', 'status',
        existing_type=sa.Enum('pending', 'paid', 'completed', 'failed', 'refunded'),
        type_=sa.Enum('pending', 'completed', 'failed', 'refunded'),
        existing_nullable=False)
    op.alter_column('PAYMENTS', 'method',
        existing_type=sa.Enum('gcash', 'bank_transfer', 'cash'),
        type_=sa.Enum('gcash', 'bank_transfer', 'cash', 'card'),
        existing_nullable=True,
        nullable=False)
