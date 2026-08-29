from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Resilient engine options based on backend dialect
_engine_kwargs = {
    "echo": (settings.APP_ENV == "development"),
    "pool_pre_ping": True,
}

if settings.DATABASE_URL and ("postgresql" in settings.DATABASE_URL or "asyncpg" in settings.DATABASE_URL):
    _engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_recycle": 300,
        "pool_timeout": 30,
    })

engine = create_async_engine(
    settings.DATABASE_URL or "sqlite+aiosqlite:///./ideagpt.db",
    **_engine_kwargs,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

