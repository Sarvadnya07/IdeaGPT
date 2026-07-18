import pytest
import os
import asyncio

# Force SQLite URL
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

# Force Celery to run in eager (synchronous) mode for testing
from app.workers.celery_app import celery_app
celery_app.conf.task_always_eager = True

# Import all models to register them with metadata
from app.db.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation

from app.core.database import engine

@pytest.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
