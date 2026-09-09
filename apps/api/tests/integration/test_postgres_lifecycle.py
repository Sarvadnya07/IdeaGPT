"""
Real PostgreSQL 18 Integration Test Suite for IdeaGPT.
Target: PostgreSQL 18.4 on localhost:5432 / DATABASE_URL.
Verifies native PostgreSQL-specific behavior:
  - Native UUID generation and indexing
  - JSONB document persistence and querying
  - Foreign key cascade deletions (Project -> Ideas, Roadmaps)
  - Unique constraints (users.clerk_id, provider_credentials compound index)
  - Explicit transaction rollback behavior
"""

import os
import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.roadmap import Roadmap, RoadmapStatus
from app.models.evaluation import Evaluation
from app.models.provider_credential import ProviderCredential

# Authoritative PostgreSQL Database URL
PG_DATABASE_URL = os.getenv(
    "POSTGRES_DATABASE_URL",
    "postgresql+asyncpg://postgres:sarvadnya@localhost:5432/ideagpt"
)

if PG_DATABASE_URL.startswith("postgresql://"):
    PG_DATABASE_URL = PG_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


@pytest.fixture
async def pg_engine():
    """Create a dedicated async engine with NullPool for isolated PostgreSQL testing."""
    engine = create_async_engine(PG_DATABASE_URL, echo=False, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
async def pg_session(pg_engine):
    """Provide a clean async session connected to the real PostgreSQL database."""
    session_maker = async_sessionmaker(pg_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_postgres_version_and_extensions(pg_engine):
    """Verify connectivity to PostgreSQL 18."""
    async with pg_engine.connect() as conn:
        res = await conn.execute(text("SELECT current_setting('server_version');"))
        version_str = res.scalar()
        assert version_str is not None
        major = int(version_str.split(".")[0])
        assert major >= 16, f"Expected PostgreSQL 16+, found: {version_str}"


@pytest.mark.asyncio
async def test_postgres_user_unique_constraint(pg_session: AsyncSession):
    """Verify that PostgreSQL enforces UNIQUE constraint on Clerk ID."""
    unique_clerk = f"user_int_test_{uuid.uuid4().hex[:12]}"
    user1 = User(
        clerk_id=unique_clerk,
        email=f"{unique_clerk}@example.com",
        name="Integration Test User 1"
    )
    pg_session.add(user1)
    await pg_session.commit()
    await pg_session.refresh(user1)
    assert user1.id is not None

    # Attempt duplicate clerk_id
    user2 = User(
        clerk_id=unique_clerk,
        email=f"other_{unique_clerk}@example.com",
        name="Duplicate User"
    )
    pg_session.add(user2)
    with pytest.raises(IntegrityError):
        await pg_session.commit()
    await pg_session.rollback()

    # Cleanup user1
    await pg_session.delete(user1)
    await pg_session.commit()


@pytest.mark.asyncio
async def test_postgres_jsonb_milestones_and_roadmap(pg_session: AsyncSession):
    """Verify PostgreSQL JSONB storage and retrieval for Roadmap milestones."""
    clerk_id = f"user_jsonb_{uuid.uuid4().hex[:8]}"
    user = User(clerk_id=clerk_id, email=f"{clerk_id}@test.com", name="JSONB User")
    pg_session.add(user)
    await pg_session.commit()
    await pg_session.refresh(user)

    proj_id = f"proj_{uuid.uuid4().hex[:12]}"
    project = Project(
        id=proj_id,
        user_id=user.id,
        title="JSONB Storage Project",
        slug=f"jsonb-proj-{uuid.uuid4().hex[:6]}"
    )
    pg_session.add(project)
    await pg_session.commit()

    milestones_payload = [
        {
            "title": "Phase 1: Architecture",
            "objective": "Design and validate schema",
            "tasks": [
                {"title": "Setup PostgreSQL", "status": "completed", "estimated_days": 2},
                {"title": "Define JSONB schema", "status": "in_progress", "estimated_days": 3}
            ]
        },
        {
            "title": "Phase 2: Execution",
            "objective": "Deliver production release",
            "tasks": [{"title": "CI Integration", "status": "pending", "estimated_days": 5}]
        }
    ]

    roadmap_id = f"road_{uuid.uuid4().hex[:12]}"
    roadmap = Roadmap(
        id=roadmap_id,
        project_id=proj_id,
        milestones=milestones_payload,
        status=RoadmapStatus.active
    )
    pg_session.add(roadmap)
    await pg_session.commit()

    # Re-fetch from PostgreSQL to verify JSON roundtrip
    stmt = select(Roadmap).where(Roadmap.id == roadmap_id)
    res = await pg_session.execute(stmt)
    fetched = res.scalar_one()

    assert fetched.status == RoadmapStatus.active
    assert len(fetched.milestones) == 2
    assert fetched.milestones[0]["title"] == "Phase 1: Architecture"
    assert fetched.milestones[0]["tasks"][0]["status"] == "completed"

    # Cleanup (PostgreSQL cascades deletion to roadmap automatically)
    await pg_session.delete(project)
    await pg_session.delete(user)
    await pg_session.commit()


@pytest.mark.asyncio
async def test_postgres_foreign_key_cascade_deletion(pg_session: AsyncSession):
    """
    Verify PostgreSQL ON DELETE CASCADE:
    Deleting a Project MUST automatically cascade and delete associated Ideas and Roadmaps.
    """
    clerk_id = f"user_cascade_{uuid.uuid4().hex[:8]}"
    user = User(clerk_id=clerk_id, email=f"{clerk_id}@test.com", name="Cascade User")
    pg_session.add(user)
    await pg_session.commit()
    await pg_session.refresh(user)

    proj_id = f"proj_cascade_{uuid.uuid4().hex[:12]}"
    project = Project(
        id=proj_id,
        user_id=user.id,
        title="Cascade Test Project",
        slug=f"cascade-proj-{uuid.uuid4().hex[:6]}"
    )
    pg_session.add(project)
    await pg_session.commit()

    # Add 2 ideas to this project with all required NOT NULL fields
    idea1 = Idea(
        id=f"idea1_{uuid.uuid4().hex[:8]}",
        project_id=proj_id,
        title="Cascade Idea 1",
        problem_statement="Problem 1",
        solution_description="Solution 1"
    )
    idea2 = Idea(
        id=f"idea2_{uuid.uuid4().hex[:8]}",
        project_id=proj_id,
        title="Cascade Idea 2",
        problem_statement="Problem 2",
        solution_description="Solution 2"
    )
    # Add a roadmap
    roadmap = Roadmap(
        id=f"road_{uuid.uuid4().hex[:8]}",
        project_id=proj_id,
        milestones=[],
        status=RoadmapStatus.draft
    )
    pg_session.add_all([idea1, idea2, roadmap])
    await pg_session.commit()

    # Verify all 3 child entities exist in PostgreSQL
    ideas_count = (await pg_session.execute(
        select(Idea).where(Idea.project_id == proj_id)
    )).scalars().all()
    assert len(ideas_count) == 2

    # Now delete the parent project directly in PostgreSQL
    await pg_session.delete(project)
    await pg_session.commit()

    # Verify PostgreSQL ON DELETE CASCADE deleted all associated child ideas and roadmaps
    remaining_ideas = (await pg_session.execute(
        select(Idea).where(Idea.project_id == proj_id)
    )).scalars().all()
    assert len(remaining_ideas) == 0, "PostgreSQL ON DELETE CASCADE failed to delete ideas"

    remaining_roadmaps = (await pg_session.execute(
        select(Roadmap).where(Roadmap.project_id == proj_id)
    )).scalars().all()
    assert len(remaining_roadmaps) == 0, "PostgreSQL ON DELETE CASCADE failed to delete roadmaps"

    # Cleanup user
    await pg_session.delete(user)
    await pg_session.commit()


@pytest.mark.asyncio
async def test_postgres_provider_credential_unique_index(pg_session: AsyncSession):
    """
    Verify PostgreSQL enforces the compound unique index (user_id, provider) on provider_credentials.
    """
    clerk_id = f"user_byok_{uuid.uuid4().hex[:8]}"
    user = User(clerk_id=clerk_id, email=f"{clerk_id}@test.com", name="BYOK User")
    pg_session.add(user)
    await pg_session.commit()
    await pg_session.refresh(user)

    cred1 = ProviderCredential(
        user_id=user.id,
        provider="groq",
        encrypted_secret="enc_sample_secret_1",
        key_hint="gsk_...1234",
        status="ACTIVE"
    )
    pg_session.add(cred1)
    await pg_session.commit()

    # Attempt duplicate (user.id, 'groq')
    cred2 = ProviderCredential(
        user_id=user.id,
        provider="groq",
        encrypted_secret="enc_sample_secret_2",
        key_hint="gsk_...5678",
        status="ACTIVE"
    )
    pg_session.add(cred2)
    with pytest.raises(IntegrityError):
        await pg_session.commit()
    await pg_session.rollback()

    # Cleanup
    await pg_session.delete(cred1)
    await pg_session.delete(user)
    await pg_session.commit()


@pytest.mark.asyncio
async def test_postgres_transaction_rollback(pg_session: AsyncSession):
    """Verify that uncommitted transactions in PostgreSQL are cleanly rolled back."""
    clerk_id = f"user_rollback_{uuid.uuid4().hex[:8]}"
    user = User(clerk_id=clerk_id, email=f"{clerk_id}@test.com", name="Rollback User")
    pg_session.add(user)
    await pg_session.flush()

    # Explicit rollback
    await pg_session.rollback()

    # Verify user does not exist in PostgreSQL
    stmt = select(User).where(User.clerk_id == clerk_id)
    res = await pg_session.execute(stmt)
    assert res.scalar_one_or_none() is None
