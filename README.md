#E0: e0.1; e0.2 -  PostgreSQL + Alembic + Temporal

Минимальный набор сервисов для запуска Temporal workflow c хранением состояния в PostgreSQL 18 и автоматическими миграциями через Alembic.

## Быстрый старт

1. **Создайте виртуальное окружение и установите зависимости**:
   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Поднимите инфраструктуру (PostgreSQL + Temporal)**:
   ```powershell
   docker-compose up -d
   ```

4. **Примените миграции** (один из вариантов):
   ```powershell
   alembic upgrade head         # вручную
   python entrypoint.py         # то же самое автоматически
   ```

5. **Стартуйте Temporal worker и API** в отдельных терминалах:
   ```powershell
   python run_worker.py
   python run_api.py
   ```

6. **Запустите тестовый workflow**:
   ```powershell
   Invoke-RestMethod -Uri http://localhost:8000/test-workflow `
     -Method Post `
     -Headers @{ "Content-Type" = "application/json" } `
     -Body '{"name": "TestUser"}'
   ```

## Проверка DoD

| Что проверить | Команда |
| --- | --- |
| PostgreSQL 18 запущен | `docker exec postgres-18 psql -U postgres -d app_db -c "SELECT version();"` |
| Alembic применяет миграции | `alembic upgrade head` → появляется запись в `alembic_version` |
| Проверка подключения из Python | `python entrypoint.py` (внутри вызывается `SELECT 1`) |
| Temporal workflow выполнен | `Invoke-RestMethod …` (см. шаг 6) возвращает `run_id` |
| Workflow завершён | `docker exec temporal-admin-tools tctl --namespace default workflow list` |

## Структура репозитория

- `docker-compose.yml` — контейнеры PostgreSQL 18, Temporal Server и admin-tools.
- `app/database.py` — SQLAlchemy engine и SessionLocal.
- `alembic/` + `alembic.ini` — конфигурация и миграции БД.
- `entrypoint.py` — ожидание БД и автоматический `alembic upgrade head`.
- `app/temporal/` — клиент и worker Temporal.
- `app/workflows/`, `app/activities/` — тестовый workflow и activity.
- `app/api/main.py` — FastAPI с endpoint `POST /test-workflow`.
- `run_worker.py`, `run_api.py` — удобные точки входа для worker и API.

## Переменные окружения

- `DATABASE_URL` (или `DATABASE_HOST/PORT/USER/PASSWORD/NAME`) — строка подключения к PostgreSQL.
- `TEMPORAL_HOST`, `TEMPORAL_PORT`, `TEMPORAL_NAMESPACE` — параметры подключения Temporal SDK (по умолчанию `localhost:7233`, `default`).

## Частые вопросы

**Нужно ли запускать Alembic, worker и API разными командами?**

Да. Alembic выполняет миграции однократно (например, в entrypoint или CI/CD), а worker и API — это отдельные процессы. Temporal по архитектуре предполагает, что worker живёт независимо и может масштабироваться отдельно от HTTP-API.
