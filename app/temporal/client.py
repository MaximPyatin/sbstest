import asyncio
import os
from typing import Optional

from temporalio.client import Client
from temporalio.service import RPCError

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost")
TEMPORAL_PORT = os.getenv("TEMPORAL_PORT", "7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

TEMPORAL_ADDRESS = f"{TEMPORAL_HOST}:{TEMPORAL_PORT}"

_client: Optional[Client] = None


async def wait_for_temporal(attempts: int = 30, delay: float = 2.0) -> None:
    """Дружелюбно стучимся к Temporal, пока он не ответит, делая паузы между подходами."""
    for attempt in range(1, attempts + 1):
        try:
            await get_temporal_client()
            return
        except (RPCError, OSError, ConnectionRefusedError) as exc:
            global _client
            _client = None
            if attempt == attempts:
                raise exc
            await asyncio.sleep(delay)


async def get_temporal_client() -> Client:
    """Отдаём готовый Temporal-клиент, создавая подключение только один раз."""
    global _client
    if _client is None:
        _client = await Client.connect(
            TEMPORAL_ADDRESS,
            namespace=TEMPORAL_NAMESPACE,
        )
    return _client


async def close_temporal_client() -> None:
    """Забываем кэшированный клиент, чтобы следующий запрос открыл свежий канал связи."""
    global _client
    _client = None

