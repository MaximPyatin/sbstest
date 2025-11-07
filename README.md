# E0.1: Настройка базы данных и миграций

PostgreSQL 18 в Docker, подключение через SQLAlchemy, автоматическое применение миграций Alembic при старте.


## Быстрый старт

1. Создать виртуальное окружение и установить зависимости:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Запустить PostgreSQL:
   ```bash
   docker-compose up -d
   ```

3. Применить миграции:
   ```bash
   alembic upgrade head
   ```

4. Запуск сервисного скрипта применит миграции автоматически:
   ```bash
   python entrypoint.py
   ```

## Структура проекта

- `docker-compose.yml` - конфигурация PostgreSQL 18
- `app/database.py` - подключение к БД, engine, session
- `alembic/` - миграции схемы базы данных
- `alembic.ini` - конфигурация Alembic
- `entrypoint.py` - автоматическое применение миграций при старте

## Переменные окружения

- `DATABASE_URL` — строка подключения к БД (по умолчанию `postgresql+psycopg://postgres:secret@localhost:5432/app_db`).
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` — альтернативная конфигурация при отсутствии `DATABASE_URL`.

## Проверка

```bash
# Версия PostgreSQL
docker exec postgres-18 psql -U postgres -d app_db -c "SELECT version();"

# Таблица версий миграций
docker exec postgres-18 psql -U postgres -d app_db -c "SELECT * FROM alembic_version;"


## Использование в Dockerfile

```dockerfile
CMD ["python", "entrypoint.py"]
```

Миграции применяются автоматически перед запуском приложения.

## Хранение данных PostgreSQL

PostgreSQL 18+ в официальных образах хранит данные в подкаталогах вида `<версия>/main` внутри `/var/lib/postgresql`. В `docker-compose.yml` используется единый том `postgres_data:/var/lib/postgresql`, что упрощает обновление через `pg_upgrade --link` и исключает конфликт точек монтирования при переходе между мажорными версиями.
