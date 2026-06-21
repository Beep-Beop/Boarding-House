"""add_approved_status_and_move_in_requested

Revision ID: aafff76a3f70
Revises: 1dd93deb66a7
Create Date: 2026-06-21 21:50:29.911944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aafff76a3f70'
down_revision: Union[str, Sequence[str], None] = '1dd93deb66a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('BOOKINGS', sa.Column('move_in_requested', sa.Boolean(), nullable=False, server_default=sa.text('0')))

    op.alter_column('BOOKINGS', 'status',
               existing_type=sa.Enum('active', 'pending', 'cancelled'),
               type_=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               existing_nullable=True)

    op.alter_column('BOOKING_HISTORY', 'old_status',
               existing_type=sa.Enum('active', 'pending', 'cancelled'),
               type_=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               existing_nullable=True)

    op.alter_column('BOOKING_HISTORY', 'new_status',
               existing_type=sa.Enum('active', 'pending', 'cancelled'),
               type_=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('BOOKING_HISTORY', 'new_status',
               existing_type=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               type_=sa.Enum('active', 'pending', 'cancelled'),
               existing_nullable=False)

    op.alter_column('BOOKING_HISTORY', 'old_status',
               existing_type=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               type_=sa.Enum('active', 'pending', 'cancelled'),
               existing_nullable=True)

    op.alter_column('BOOKINGS', 'status',
               existing_type=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               type_=sa.Enum('active', 'pending', 'cancelled'),
               existing_nullable=True)

    op.drop_column('BOOKINGS', 'move_in_requested')
