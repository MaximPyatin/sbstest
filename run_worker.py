"""Простой запуск Temporal worker без магии — используем в Docker и локально."""

import asyncio
from app.temporal.worker import run_worker

if __name__ == "__main__":
    asyncio.run(run_worker())



