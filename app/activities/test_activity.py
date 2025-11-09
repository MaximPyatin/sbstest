from temporalio import activity
import asyncio


@activity.defn(name="TestActivity")
async def sample_activity(name: str) -> str:
    """Мини-activity для демо: делаем паузу и отвечаем тёплым приветом по имени."""
    activity.logger.info(f"Выполнение activity для {name}")
    
    await asyncio.sleep(2)
    
    result = f"Привет, {name}! Activity успешно выполнена."
    activity.logger.info(f"Activity завершена: {result}")
    
    return result



