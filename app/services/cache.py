import os
from typing import Optional

from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: Optional[Redis] = None


async def connect_redis() -> Redis:
    """Создаёт подключение к Redis с ленивой инициализацией и проверкой ping."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await _redis.ping()
    return _redis


async def get_redis() -> Redis:
    """Возвращает активное подключение Redis и проверяет ping."""
    client = await connect_redis()
    pong = await client.ping()
    if pong not in ("PONG", True):
        raise RuntimeError(f"Unexpected Redis PING response: {pong}")
    return client


async def close_redis() -> None:
    """Закрывает соединение с Redis и сбрасывает кэшированный клиент."""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


async def set_value(key: str, value: str) -> None:
    """Сохраняет строковое значение по ключу в Redis."""
    client = await get_redis()
    await client.set(key, value)


async def get_value(key: str) -> Optional[str]:
    """Читает строковое значение из Redis по ключу."""
    client = await get_redis()
    return await client.get(key)

