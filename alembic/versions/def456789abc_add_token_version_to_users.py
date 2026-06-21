"""add_token_version_to_users

Revision ID: def456789abc
Revises: 49a657242faa
Create Date: 2026-06-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'def456789abc'
down_revision: Union[str, Sequence[str], None] = '49a657242faa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('USERS', sa.Column('token_version', sa.Integer(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    op.drop_column('USERS', 'token_version')
