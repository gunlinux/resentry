"""add password field to users table

Revision ID: 15e551e5c30d
Revises: 71d60aecf1b9
Create Date: 2025-11-26 05:08:12.418625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15e551e5c30d'
down_revision: Union[str, Sequence[str], None] = '71d60aecf1b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add password column to users table as nullable initially
    op.add_column('users', sa.Column('password', sa.String(), nullable=True))

    # Set a default password for existing users (required since field is non-nullable in the model)
    # In production, you would want to ensure all users reset their passwords
    op.execute("UPDATE users SET password = '' WHERE password IS NULL")

    # Now make the column non-nullable
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('password', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'password')
