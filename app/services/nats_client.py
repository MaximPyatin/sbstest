import asyncio
import os
from typing import Optional

from nats.aio.client import Client as NATS


NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
NATS_SUBJECT = os.getenv("NATS_SUBJECT", "backup.test")

_nats = NATS()
_message_queue: "asyncio.Queue[bytes]" = asyncio.Queue()
_subscription_sid: Optional[int] = None


async def connect_nats() -> NATS:
    """Устанавливает соединение с NATS и подписывается на базовый subject."""
    global _subscription_sid
    if not _nats.is_connected:
        await _nats.connect(servers=[NATS_URL])
        _subscription_sid = await _nats.subscribe(NATS_SUBJECT, cb=_message_handler)
    return _nats


async def get_nats() -> NATS:
    """Возвращает активное соединение NATS, удостоверяясь, что оно установлено."""
    client = await connect_nats()
    if not client.is_connected:
        raise RuntimeError("NATS connection is not active")
    return client


async def _message_handler(msg) -> None:
    """Кладёт входящее сообщение в очередь для последующей обработки."""
    await _message_queue.put(msg.data)


async def publish_message(subject: str, payload: bytes) -> None:
    """Отправляет сообщение в NATS и дожидается подтверждения публикации."""
    client = await get_nats()
    await client.publish(subject, payload)
    await client.flush()


async def wait_for_message(timeout: float = 1.0) -> bytes:
    """Получает следующее сообщение из очереди, ожидая не дольше таймаута."""
    await get_nats()
    return await asyncio.wait_for(_message_queue.get(), timeout=timeout)


async def close_nats() -> None:
    """Отписывается от subject и корректно завершает соединение с NATS."""
    global _subscription_sid
    if _nats.is_connected:
        if _subscription_sid is not None:
            await _nats.unsubscribe(_subscription_sid)
            _subscription_sid = None
        await _nats.drain()


def clear_pending_messages() -> None:
    """Очищает очередь ожидающих сообщений из тестовой подписки."""
    while not _message_queue.empty():
        _message_queue.get_nowait()

