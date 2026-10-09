"""add_partial_unique_index_active_evaluations

Enforces at the database level the application invariant that an idea has at
most one active (PENDING / RUNNING) evaluation. Closes the check-then-act race
in EvaluationCoordinator.create_evaluation where two concurrent POSTs could
both pass the SELECT guard and insert duplicate active evaluations.

Partial index: only rows whose status is an active state participate, so
completed/failed/cancelled history is unaffected.

SQLite supports partial indexes, so local dev (aiosqlite) and CI PostgreSQL
both accept this migration.

Revision ID: f4a5b6c7d8e9
Revises: d2e3f4a5b6c7
Create Date: 2026-09-14 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text


# revision identifiers, used by Alembic.
revision: str = 'f4a5b6c7d8e9'
down_revision: Union[str, Sequence[str], None] = 'e3f4a5b6c7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'uq_evaluations_active_per_idea',
        'evaluations',
        ['idea_id'],
        unique=True,
        postgresql_where=sa_text("status IN ('PENDING', 'RUNNING', 'QUEUED')"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_evaluations_one_active_per_idea', table_name='evaluations')
