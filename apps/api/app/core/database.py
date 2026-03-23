from __future__ import annotations

import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.models.base import Base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@db:5432/lens",
)
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

engine = create_async_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


__all__ = ["engine", "async_session", "get_db", "lifespan_session", "Base"]


@asynccontextmanager
async def lifespan_session() -> AsyncSession:
    """Reusable async context manager for scripts and background jobs."""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_db():
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
