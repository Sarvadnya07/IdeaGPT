"""add_ai_artifacts_table

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-08-27 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2e3f4a5b6c7'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'ai_artifacts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('idea_id', sa.String(length=36), nullable=True),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='Untitled AI Artifact'),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='groq'),
        sa.Column('model', sa.String(length=100), nullable=False, server_default='openai/gpt-oss-120b'),
        sa.Column('requested_provider', sa.String(length=50), nullable=True),
        sa.Column('requested_model', sa.String(length=100), nullable=True),
        sa.Column('fallback_used', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('fallback_reason', sa.String(length=500), nullable=True),
        sa.Column('execution_type', sa.String(length=30), nullable=False, server_default='REAL_PROVIDER'),
        sa.Column('content_payload', sa.JSON(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('token_usage', sa.Integer(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['idea_id'], ['ideas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_artifacts_user_id'), 'ai_artifacts', ['user_id'], unique=False)
    op.create_index(op.f('ix_ai_artifacts_project_id'), 'ai_artifacts', ['project_id'], unique=False)
    op.create_index(op.f('ix_ai_artifacts_idea_id'), 'ai_artifacts', ['idea_id'], unique=False)
    op.create_index(op.f('ix_ai_artifacts_artifact_type'), 'ai_artifacts', ['artifact_type'], unique=False)
    op.create_index(op.f('ix_ai_artifacts_created_at'), 'ai_artifacts', ['created_at'], unique=False)
    op.create_index('idx_user_artifact_type', 'ai_artifacts', ['user_id', 'artifact_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_user_artifact_type', table_name='ai_artifacts')
    op.drop_index(op.f('ix_ai_artifacts_created_at'), table_name='ai_artifacts')
    op.drop_index(op.f('ix_ai_artifacts_artifact_type'), table_name='ai_artifacts')
    op.drop_index(op.f('ix_ai_artifacts_idea_id'), table_name='ai_artifacts')
    op.drop_index(op.f('ix_ai_artifacts_project_id'), table_name='ai_artifacts')
    op.drop_index(op.f('ix_ai_artifacts_user_id'), table_name='ai_artifacts')
    op.drop_table('ai_artifacts')
