
## Платформа и CI/CD 

E0.1–E0.3: PostgreSQL, Temporal, Redis, NATS

Набор сервисов для старта платформы: PostgreSQL 18 с Alembic, Temporal Server + worker, Redis и NATS, а также FastAPI для проверки интеграций.

## Быстрый старт

1. **Создайте виртуальное окружение и установите зависимости**:
   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Поднимите контейнеры (PostgreSQL, Temporal, Redis, NATS)**:
   ```powershell
   docker-compose up -d
   ```

3. **Примените миграции**:
   ```powershell
   alembic upgrade head   # вручную
   python entrypoint.py   # автоматически + SELECT 1
   ```

4. **Запустите worker и API** (разные терминалы):
   ```powershell
   python run_worker.py
   python run_api.py
   ```

5. **Проверьте сервисы**:
   ```powershell
   # Workflow + Temporal (возвращает run_id / workflow_id)
   Invoke-RestMethod -Uri http://localhost:8000/test-workflow `
     -Method Post `
     -Headers @{ "Content-Type" = "application/json" } `
     -Body '{"name": "TestUser"}'

  # NATS (publish + subscribe за 1 секунду)
   Invoke-RestMethod -Uri http://localhost:8000/nats/test `
     -Method Post `
     -Headers @{ "Content-Type" = "application/json" } `
     -Body '{"message": "data"}'

  # Redis (set/get)
   Invoke-RestMethod -Uri http://localhost:8000/redis/test `
     -Method Post `
     -Headers @{ "Content-Type" = "application/json" } `
     -Body '{"key": "test", "value": "val"}'
   ```

## Проверка DoD

| Что проверить | Команда |
| --- | --- |
| PostgreSQL 18 запущен | `docker exec postgres-18 psql -U postgres -d app_db -c "SELECT version();"` |
| Alembic создаёт `alembic_version` | `alembic upgrade head` |
| Авто-миграции и `SELECT 1` | `python entrypoint.py` |
| Workflow получает `run_id` | `Invoke-RestMethod ... /test-workflow` |
| Workflow завершён в Temporal | `docker exec temporal-admin-tools tctl --namespace default workflow list` |
| NATS CLI | `docker exec nats nats pub test hello` + `docker exec nats nats sub test` |
| Redis CLI и персистентность | `docker exec redis redis-cli set key val` + `docker exec redis redis-cli get key` |

## Структура

- `docker-compose.yml` — контейнеры PostgreSQL, Temporal Server, Temporal admin-tools, Redis, NATS.
- `alembic/`, `alembic.ini`, `entrypoint.py` — миграции и автоматический запуск.
- `app/database.py` — SQLAlchemy engine/Session.
- `app/temporal/` — клиент и worker Temporal.
- `app/services/` — вспомогательные клиенты Redis (`cache.py`) и NATS (`nats_client.py`).
- `app/workflows/`, `app/activities/` — тестовый workflow и activity.
- `app/api/main.py` — FastAPI (`/test-workflow`, `/nats/test`, `/redis/test`).
- `run_worker.py`, `run_api.py` — точки запуска worker и API.

## Переменные окружения

- `DATABASE_URL` или `DATABASE_HOST/PORT/USER/PASSWORD/NAME` — PostgreSQL.
- `TEMPORAL_HOST`, `TEMPORAL_PORT`, `TEMPORAL_NAMESPACE` — Temporal SDK (по умолчанию `localhost:7233`, `default`).
- `REDIS_URL` — адрес Redis (`redis://localhost:6379/0` по умолчанию).
- `NATS_URL`, `NATS_SUBJECT` — подключение к NATS (`nats://localhost:4222`, `backup.test`).
