from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


@workflow.defn(name="TestWorkflow")
class TestWorkflow:
    """Небольшой учебный workflow: принимает имя, дергает activity и возвращает приветствие."""
    @workflow.run
    async def run(self, name: str) -> str:
        """Берём имя, зовём activity, ждём пару секунд и возвращаем дружелюбный отклик."""
        workflow.logger.info(f"Запуск workflow для {name}")
        
        from app.activities.test_activity import sample_activity
        
        result = await workflow.execute_activity(
            sample_activity,
            name,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        
        workflow.logger.info(f"Workflow завершен с результатом: {result}")
        return result

