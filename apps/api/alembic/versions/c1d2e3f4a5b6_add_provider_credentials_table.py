"""add_provider_credentials_table

Revision ID: c1d2e3f4a5b6
Revises: 470ae65e8c8e
Create Date: 2026-08-27 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = '470ae65e8c8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'provider_credentials',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('encrypted_secret', sa.String(length=512), nullable=False),
        sa.Column('key_hint', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE'),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_provider_cred', 'provider_credentials', ['user_id', 'provider'], unique=True)
    op.create_index(op.f('ix_provider_credentials_provider'), 'provider_credentials', ['provider'], unique=False)
    op.create_index(op.f('ix_provider_credentials_user_id'), 'provider_credentials', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_provider_credentials_user_id'), table_name='provider_credentials')
    op.drop_index(op.f('ix_provider_credentials_provider'), table_name='provider_credentials')
    op.drop_index('idx_user_provider_cred', table_name='provider_credentials')
    op.drop_table('provider_credentials')
