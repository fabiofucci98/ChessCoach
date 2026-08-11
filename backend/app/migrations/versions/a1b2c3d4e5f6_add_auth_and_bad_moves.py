"""Add auth and bad moves

Revision ID: a1b2c3d4e5f6
Revises: 5830b0149400
Create Date: 2026-08-10 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5830b0149400'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add hashed_password column to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=False, server_default=''))

    # Create bad_moves table
    op.create_table('bad_moves',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('game_id', sa.UUID(), nullable=False),
    sa.Column('fen', sa.Text(), nullable=False),
    sa.Column('move_played', sa.String(length=20), nullable=False),
    sa.Column('best_move', sa.String(length=20), nullable=False),
    sa.Column('evaluation_before', sa.Float(), nullable=False),
    sa.Column('evaluation_after', sa.Float(), nullable=False),
    sa.Column('move_number', sa.Integer(), nullable=False),
    sa.Column('counter', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('bad_moves')
    op.drop_column('users', 'hashed_password')