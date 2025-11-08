from temporalio import activity
import asyncio


@activity.defn(name="TestActivity")
async def test_activity(name: str) -> str:
    """Проверочная activity, которая ждёт 2 секунды и возвращает приветствие."""
    activity.logger.info(f"Выполнение activity для {name}")
    
    await asyncio.sleep(2)
    
    result = f"Привет, {name}! Activity успешно выполнена."
    activity.logger.info(f"Activity завершена: {result}")
    
    return result



