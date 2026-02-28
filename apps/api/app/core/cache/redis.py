import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
)

# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     decode_responses=True,
# )

async def add_revoked_session(session_id: str, ttl_seconds: int):
    await redis_client.set(
        f"revoked:{session_id}",
        "1",
        ex=ttl_seconds,
    )

async def is_session_revoked(session_id: str) -> bool:
    value = await redis_client.get(f"revoked:{session_id}")
    return value is not None
