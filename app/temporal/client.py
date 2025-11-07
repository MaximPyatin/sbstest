import os
import time
from temporalio.client import Client
from temporalio.service import RPCError

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost")
TEMPORAL_PORT = os.getenv("TEMPORAL_PORT", "7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

TEMPORAL_ADDRESS = f"{TEMPORAL_HOST}:{TEMPORAL_PORT}"


async def wait_for_temporal(attempts: int = 30, delay: float = 2.0) -> None:
    for attempt in range(1, attempts + 1):
        try:
            client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
            return
        except (RPCError, OSError, ConnectionRefusedError) as exc:
            if attempt == attempts:
                raise exc
            time.sleep(delay)


async def get_temporal_client() -> Client:
    client = await Client.connect(
        TEMPORAL_ADDRESS,
        namespace=TEMPORAL_NAMESPACE,
    )
    return client

