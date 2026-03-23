from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import fakeredis.aioredis

os.environ.setdefault("RATE_LIMIT_STORAGE_URI", "memory://")
os.environ.setdefault("DISABLE_RATE_LIMITS", "1")
os.environ.setdefault("PYTEST_ASYNCIO_MODE", "auto")

from app.main import app
from app.core.database import get_db
from app.core.models.base import Base
from app.core.models.user import User
from app.core.models.refresh_token import RefreshToken
from app.core.cache import redis as redis_cache


@pytest_asyncio.fixture
async def api_client():
    """Provide an ASGI test client backed by isolated SQLite + fake Redis."""
    database_url = "sqlite+aiosqlite:///file::memory:?cache=shared"

    sync_engine = create_engine(
        "sqlite:///file::memory:?cache=shared", connect_args={"uri": True}
    )
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    engine = create_async_engine(
        database_url,
        future=True,
        connect_args={"check_same_thread": False, "uri": True},
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    original_redis = redis_cache.redis_client
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    redis_cache.redis_client = fake_redis

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client, session_maker, fake_redis

    app.dependency_overrides = previous_overrides
    redis_cache.redis_client = original_redis
    await engine.dispose()
    # In-memory DB; nothing to clean up.


async def _verify_user(session_maker: async_sessionmaker[AsyncSession], email: str):
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.email == email))
        user.is_verified = True
        await session.commit()


async def _expire_refresh_tokens(session_maker: async_sessionmaker[AsyncSession]):
    async with session_maker() as session:
        token = await session.scalar(select(RefreshToken))
        token.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        await session.commit()


@pytest.mark.asyncio
async def test_login_requires_verified_user(api_client):
    client, _, _ = api_client

    payload = {"email": "unverified@example.com", "username": "unverified", "password": "Secure123"}
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 200

    login_resp = await client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login_resp.status_code == 403


@pytest.mark.asyncio
async def test_successful_login_and_refresh_rotation(api_client):
    client, session_maker, _ = api_client

    payload = {"email": "user@example.com", "username": "useralpha", "password": "Secure123"}
    await client.post("/auth/register", json=payload)
    await _verify_user(session_maker, payload["email"])

    login_resp = await client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login_resp.status_code == 200

    original_refresh = client.cookies.get("refresh_token")
    assert original_refresh

    refresh_resp = await client.post("/auth/refresh")
    assert refresh_resp.status_code == 200

    rotated_refresh = client.cookies.get("refresh_token")
    assert rotated_refresh and rotated_refresh != original_refresh

    replay_resp = await client.post("/auth/refresh", cookies={"refresh_token": original_refresh})
    assert replay_resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_denied_when_token_expired(api_client):
    client, session_maker, _ = api_client

    payload = {"email": "expire@example.com", "username": "expireuser", "password": "Expire123"}
    await client.post("/auth/register", json=payload)
    await _verify_user(session_maker, payload["email"])

    login_resp = await client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login_resp.status_code == 200

    await _expire_refresh_tokens(session_maker)

    refresh_resp = await client.post("/auth/refresh")
    assert refresh_resp.status_code == 401
