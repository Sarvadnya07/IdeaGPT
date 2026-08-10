"""add evaluation history and stale recovery

Revision ID: b3c4d5e6f7g8
Revises: a2b3c4d5e6f7
Create Date: 2026-08-10 16:00:00.000000

Rationale:
    Sprint 2.6 introduces the persistent audit log table `evaluation_history`
    to record every lifecycle state transition, stage progress, failure event,
    and stale execution recovery in PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7g8'
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'evaluation_history',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('evaluation_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('from_status', sa.String(length=32), nullable=True),
        sa.Column('to_status', sa.String(length=32), nullable=True),
        sa.Column('progress', sa.String(length=64), nullable=True),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evaluation_history_evaluation_id'), 'evaluation_history', ['evaluation_id'], unique=False)
    op.create_index(op.f('ix_evaluation_history_event_type'), 'evaluation_history', ['event_type'], unique=False)
    op.create_index(op.f('ix_evaluation_history_created_at'), 'evaluation_history', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_evaluation_history_created_at'), table_name='evaluation_history')
    op.drop_index(op.f('ix_evaluation_history_event_type'), table_name='evaluation_history')
    op.drop_index(op.f('ix_evaluation_history_evaluation_id'), table_name='evaluation_history')
    op.drop_table('evaluation_history')
