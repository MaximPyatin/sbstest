import sys
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database import DATABASE_URL, engine

BASE_DIR = Path(__file__).resolve().parent


def build_config() -> Config:
    config = Config(str(BASE_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BASE_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    return config


def wait_for_database(attempts: int = 10, delay: float = 3.0) -> None:
    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            if attempt == attempts:
                raise exc
            time.sleep(delay)


def apply_migrations() -> None:
    config = build_config()
    command.upgrade(config, "head")


def main() -> None:
    try:
        wait_for_database()
        apply_migrations()
        print("Миграции Alembic успешно применены.")
    except Exception as exc:
        print(f"Ошибка применения миграций: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()