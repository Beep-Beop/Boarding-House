"""rename type to notif_type in notifications

Revision ID: abc1234def56
Revises: 275382b2f368
Create Date: 2026-06-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'abc1234def56'
down_revision: Union[str, Sequence[str], None] = '275382b2f368'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('NOTIFICATIONS', 'type', new_column_name='notif_type')


def downgrade() -> None:
    op.alter_column('NOTIFICATIONS', 'notif_type', new_column_name='type')
