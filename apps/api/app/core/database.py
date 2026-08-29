import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Resilient engine options based on backend dialect
_engine_kwargs = {
    "echo": (settings.APP_ENV == "development"),
    "pool_pre_ping": True,
}

db_url = settings.async_database_url

is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
default_pool_size = 5 if is_serverless else 20
default_max_overflow = 5 if is_serverless else 10

if "postgresql" in db_url or "asyncpg" in db_url:
    _engine_kwargs.update({
        "pool_size": int(os.getenv("DB_POOL_SIZE", default_pool_size)),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", default_max_overflow)),
        "pool_recycle": 180 if is_serverless else 300,
        "pool_timeout": 30,
    })

engine = create_async_engine(
    db_url,
    **_engine_kwargs,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

