import os
from typing import Optional

from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: Optional[Redis] = None


async def connect_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await _redis.ping()
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis is not connected")
    return _redis


async def set_value(key: str, value: str) -> None:
    await get_redis().set(key, value)


async def get_value(key: str) -> Optional[str]:
    return await get_redis().get(key)

