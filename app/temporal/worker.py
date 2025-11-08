import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from app.temporal.client import TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, wait_for_temporal
from app.workflows.test_workflow import TestWorkflow
from app.activities.test_activity import sample_activity


async def run_worker():
    """Запускает Temporal worker с тестовым workflow и activity."""
    print(f"Ожидание подключения к Temporal на {TEMPORAL_ADDRESS}...")
    await wait_for_temporal()
    print(f"Подключение к Temporal установлено, namespace: {TEMPORAL_NAMESPACE}")
    
    client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
    
    worker = Worker(
        client,
        task_queue="test-task-queue",
        workflows=[TestWorkflow],
        activities=[sample_activity],
    )
    
    print("Temporal Worker запущен, ожидание задач...")
    
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())

