"""Enforce evaluation and AI-task concurrency/idempotency invariants.

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-09-18 00:00:00.000000

BACKEND-01 finding F-06 (proven live by probe P4):
  - evaluations and ai_tasks had ZERO unique constraints.
  - create_evaluation and create_task used read-then-insert check-then-act with no
    lock, so concurrent requests could create duplicate active evaluations and
    duplicate idempotent tasks.
  - update_task_status was a non-atomic read-modify-write.

This migration adds partial unique indexes that enforce the invariants at the
database layer:

  * One active evaluation per idea (status IN PENDING / RUNNING / QUEUED).
  * One AI task per (user_id, idempotency_key) when an idempotency key is present.

Both indexes are partial so completed/failed/cancelled rows do not block retries.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, Sequence[str], None] = 'd2e3f4a5b6c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _reconcile_pre_existing_violations() -> None:
    """
    PRODUCT-01 P-09: these invariants were previously UNENFORCED, so an existing
    database may already violate them. CREATE UNIQUE INDEX would abort on that
    data and leave a half-applied migration. Reconcile deterministically first.

    Both statements are idempotent: re-running them is a no-op once the data is
    consistent. Kept dialect-portable (window functions, || concatenation) so the
    migration also runs on the SQLite used by the test suite.
    """
    # At most one ACTIVE evaluation per idea: keep the newest, cancel the rest.
    op.execute(
        """
        UPDATE evaluations
        SET status = 'CANCELLED',
            error_message = COALESCE(error_message || ' | ', '')
                || 'Reconciled by migration e3f4a5b6c7d8: superseded by a newer active evaluation for the same idea.'
        WHERE status IN ('PENDING', 'RUNNING', 'QUEUED')
          AND id NOT IN (
              SELECT id FROM (
                  SELECT id,
                         ROW_NUMBER() OVER (
                             PARTITION BY idea_id
                             ORDER BY created_at DESC, id DESC
                         ) AS rn
                  FROM evaluations
                  WHERE status IN ('PENDING', 'RUNNING', 'QUEUED')
              ) ranked
              WHERE rn = 1
          )
        """
    )

    # One task per (user_id, idempotency_key): keep the earliest, release the key
    # on the duplicates rather than deleting rows (preserves task history).
    op.execute(
        """
        UPDATE ai_tasks
        SET idempotency_key = NULL
        WHERE idempotency_key IS NOT NULL
          AND id NOT IN (
              SELECT id FROM (
                  SELECT id,
                         ROW_NUMBER() OVER (
                             PARTITION BY user_id, idempotency_key
                             ORDER BY created_at ASC, id ASC
                         ) AS rn
                  FROM ai_tasks
                  WHERE idempotency_key IS NOT NULL
              ) ranked
              WHERE rn = 1
          )
        """
    )


def upgrade() -> None:
    _reconcile_pre_existing_violations()

    # Partial unique index: at most one active evaluation per idea.
    op.create_index(
        "uq_evaluations_active_per_idea",
        "evaluations",
        ["idea_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('PENDING', 'RUNNING', 'QUEUED')"),
    )

    # Partial unique index: idempotency-key deduplication per user.
    op.create_index(
        "uq_ai_tasks_user_idempotency",
        "ai_tasks",
        ["user_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    # Supporting composite indexes for the hot ownership probes.
    op.create_index(
        "ix_evaluations_idea_id_status",
        "evaluations",
        ["idea_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_ai_tasks_user_id_created_at",
        "ai_tasks",
        ["user_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ai_tasks_user_id_created_at", table_name="ai_tasks")
    op.drop_index("ix_evaluations_idea_id_status", table_name="evaluations")
    op.drop_index("uq_ai_tasks_user_idempotency", table_name="ai_tasks")
    op.drop_index("uq_evaluations_active_per_idea", table_name="evaluations")