"""add_move_in_requested_to_booking_history_enum

Revision ID: 49a657242faa
Revises: aafff76a3f70
Create Date: 2026-06-21 22:42:20.381579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49a657242faa'
down_revision: Union[str, Sequence[str], None] = 'aafff76a3f70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('BOOKING_HISTORY', 'new_status',
               existing_type=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               type_=sa.Enum('active', 'pending', 'approved', 'cancelled', 'move_in_requested'),
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('BOOKING_HISTORY', 'new_status',
               existing_type=sa.Enum('active', 'pending', 'approved', 'cancelled', 'move_in_requested'),
               type_=sa.Enum('active', 'pending', 'approved', 'cancelled'),
               existing_nullable=False)
