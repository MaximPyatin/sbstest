import os
from typing import Optional

from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: Optional[Redis] = None


async def connect_redis() -> Redis:
    """Лениво открываем соединение с Redis и сразу проверяем, что он отвечает."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await _redis.ping()
    return _redis


async def get_redis() -> Redis:
    """Достаём готовый Redis-клиент и убеждаемся, что пинг проходит без сюрпризов."""
    client = await connect_redis()
    pong = await client.ping()
    if pong not in ("PONG", True):
        raise RuntimeError(f"Unexpected Redis PING response: {pong}")
    return client


async def close_redis() -> None:
    """Аккуратно закрываем соединение и очищаем кэш, чтобы не держать лишние коннекты."""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


async def set_value(key: str, value: str) -> None:
    """Кладём строку в Redis по заданному ключу, как в маленький временный блокнот."""
    client = await get_redis()
    await client.set(key, value)


async def get_value(key: str) -> Optional[str]:
    """Читаем обратно, что лежит в Redis, если ключ ещё не протух."""
    client = await get_redis()
    return await client.get(key)

