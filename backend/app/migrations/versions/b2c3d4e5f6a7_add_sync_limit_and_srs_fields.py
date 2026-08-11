"""Add sync_limit and SRS fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-10 21:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add sync_limit to users
    op.add_column('users', sa.Column('sync_limit', sa.Integer(), nullable=False, server_default='50'))

    # Add SRS + fen_before fields to bad_moves
    op.add_column('bad_moves', sa.Column('fen_before', sa.Text(), nullable=True))
    op.add_column('bad_moves', sa.Column('easiness_factor', sa.Float(), nullable=False, server_default='2.5'))
    op.add_column('bad_moves', sa.Column('interval', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('bad_moves', sa.Column('repetitions', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('bad_moves', sa.Column('next_review_at', sa.DateTime(), nullable=True))
    op.add_column('bad_moves', sa.Column('last_reviewed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'sync_limit')
    op.drop_column('bad_moves', 'fen_before')
    op.drop_column('bad_moves', 'easiness_factor')
    op.drop_column('bad_moves', 'interval')
    op.drop_column('bad_moves', 'repetitions')
    op.drop_column('bad_moves', 'next_review_at')
    op.drop_column('bad_moves', 'last_reviewed_at')