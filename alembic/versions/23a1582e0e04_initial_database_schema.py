"""Initial database schema

Revision ID: 23a1582e0e04
Revises:
Create Date: 2025-11-15 05:48:36.992890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '23a1582e0e04'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('telegram_chat_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('lang', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)

    # Create envelopes table
    op.create_table(
        'envelopes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('payload', sa.LargeBinary(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('dsn', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_envelopes_id'), 'envelopes', ['id'], unique=False)

    # Create envelope_items table
    op.create_table(
        'envelope_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('payload', sa.LargeBinary(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['envelopes.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_envelope_items_id'), 'envelope_items', ['id'], unique=False)
    op.create_index(op.f('ix_envelope_items_item_id'), 'envelope_items', ['item_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_index(op.f('ix_envelope_items_item_id'), table_name='envelope_items')
    op.drop_index(op.f('ix_envelope_items_id'), table_name='envelope_items')
    op.drop_table('envelope_items')

    op.drop_index(op.f('ix_envelopes_id'), table_name='envelopes')
    op.drop_table('envelopes')

    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_table('projects')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_table('users')
