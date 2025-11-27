"""modify password field constraints on users table

Revision ID: 15e551e5c30d
Revises: 71d60aecf1b9
Create Date: 2025-11-26 05:08:12.418625

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "15e551e5c30d"
down_revision: Union[str, Sequence[str], None] = "71d60aecf1b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Since the password column already exists from the previous migration,
    # we just ensure the constraints are correct
    # Update any null passwords to empty string if they exist
    op.execute("UPDATE users SET password = '' WHERE password IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Don't drop the password column as it's needed for the model
    # Just leave it as is since the previous migration added it
    pass
