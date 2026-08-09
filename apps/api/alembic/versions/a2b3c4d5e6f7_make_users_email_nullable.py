"""make users email nullable

Revision ID: a2b3c4d5e6f7
Revises: 9d1281023f9b
Create Date: 2026-08-10 00:28:00.000000

Rationale:
    Clerk session JWTs do not include the user's email address by default.
    The email claim is only present when explicitly added to the session
    token template in the Clerk dashboard.  Making this column nullable
    removes the need to fabricate placeholder email addresses (e.g.
    clerk_id@placeholder.com) on first login, which were a data integrity
    violation and a security anti-pattern.

    To populate email automatically, either:
      1. Add `{{ user.primary_email_address }}` to the Clerk session token
         template (Clerk Dashboard → Configure → Sessions → Customize).
      2. Handle the clerk/user.created webhook and populate email from
         the webhook payload.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2b3c4d5e6f7'
down_revision = '9d1281023f9b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make users.email nullable
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'email',
            existing_type=sa.String(),
            nullable=True,
        )


def downgrade() -> None:
    # Revert users.email to non-nullable.
    # WARNING: this will fail if any rows have NULL email.
    # Run: UPDATE users SET email = clerk_id || '@placeholder.invalid'
    # WHERE email IS NULL; before downgrading.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'email',
            existing_type=sa.String(),
            nullable=False,
        )
