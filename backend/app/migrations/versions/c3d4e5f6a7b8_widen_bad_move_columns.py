"""Widen bad_moves move columns to String(50)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-11 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('bad_moves', 'move_played',
                    existing_type=sa.String(length=20), type_=sa.String(length=50),
                    existing_nullable=False)
    op.alter_column('bad_moves', 'best_move',
                    existing_type=sa.String(length=20), type_=sa.String(length=50),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('bad_moves', 'move_played',
                    existing_type=sa.String(length=50), type_=sa.String(length=20),
                    existing_nullable=False)
    op.alter_column('bad_moves', 'best_move',
                    existing_type=sa.String(length=50), type_=sa.String(length=20),
                    existing_nullable=False)
