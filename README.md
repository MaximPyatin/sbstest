
## Платформа и CI/CD 

E0.1–E0.3: PostgreSQL, Temporal, Redis, NATS  
E0.4: FastAPI Core API, логирование, DI

Набор сервисов для старта платформы: PostgreSQL 18 с Alembic, Temporal Server + worker, Redis и NATS, а также FastAPI для проверки интеграций.  
Core API предоставляет каркас CP: эндпоинты `/health`, `/version`, middleware с `request_id`, и DI-обёртки для Temporal, NATS, Redis.

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

   # Health-check и инициализация DI (Temporal, NATS, Redis)
   Invoke-RestMethod -Uri http://localhost:8000/health

   # Версия и build из git или переменной окружения APP_BUILD
   Invoke-RestMethod -Uri http://localhost:8000/version

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

  # Infrastructure setting stored в PostgreSQL
  Invoke-RestMethod -Uri http://localhost:8000/settings/core.version
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
| Core API health | `Invoke-RestMethod http://localhost:8000/health` |
| Версия приложения | `Invoke-RestMethod http://localhost:8000/version` |
| Согласованность настроек в БД | `Invoke-RestMethod http://localhost:8000/settings/core.version` |

## Структура

- `docker-compose.yml` — контейнеры PostgreSQL, Temporal Server, Temporal admin-tools, Redis, NATS.
- `alembic/`, `alembic.ini`, `entrypoint.py` — миграции и автоматический запуск.
- `app/database.py` — SQLAlchemy engine/Session.
- `app/models/` — SQLAlchemy-модели инфраструктуры (например, `SystemSetting`).
- `app/temporal/` — клиент и worker Temporal.
- `app/services/` — вспомогательные клиенты Redis (`cache.py`) и NATS (`nats_client.py`).
- `app/workflows/`, `app/activities/` — тестовый workflow и activity.
- `app/api/main.py` — FastAPI (`/health`, `/version`, `/test-workflow`, `/nats/test`, `/redis/test`, `/settings/{key}`), middleware и DI.
- `run_worker.py`, `run_api.py` — точки запуска worker и API.

## Переменные окружения

- `DATABASE_URL` или `DATABASE_HOST/PORT/USER/PASSWORD/NAME` — PostgreSQL.
- `TEMPORAL_HOST`, `TEMPORAL_PORT`, `TEMPORAL_NAMESPACE` — Temporal SDK (по умолчанию `localhost:7233`, `default`).
- `REDIS_URL` — адрес Redis (`redis://localhost:6379/0` по умолчанию).
- `NATS_URL`, `NATS_SUBJECT` — подключение к NATS (`nats://localhost:4222`, `backup.test`).

## CI/CD конвейер

GitHub Actions workflow `.github/workflows/ci.yml` реализует этап E0.5:

- `pytest` — юнит/интеграционные тесты.
- `docker/build-push-action` — сборка multi-stage образа (см. `Dockerfile`) и публикация в GHCR.
- `anchore/sbom-action` — генерация SBOM (`sbom.spdx.json`) на основе Syft.
- `aquasecurity/trivy-action` — сканирование уязвимостей.
- `cosign` — подпись образа (по digest).
- `scripts/deploy_test.sh` — деплой в тестовый Kubernetes-кластер.

### Секреты и переменные репозитория

| Название | Обязательность | Описание |
| --- | --- | --- |
| `COSIGN_PRIVATE_KEY` | ✅ | Приватный ключ Cosign (PEM), сохранённый в секрете. Используется через `env://COSIGN_PRIVATE_KEY`. |
| `COSIGN_PASSWORD` | ✅ | Пароль к ключу Cosign. |
| `KUBE_CONFIG_B64` | ✅ для деплоя | kubeconfig в Base64. Скрипт разворачивания декодирует его во временный файл. |
| `KUBE_NAMESPACE` | ➖ | Тестовый namespace (по умолчанию `default`). |

Для доступа к GHCR в кластере необходимо добавить secret `ghcr-credentials`, который использует Kubernetes deployment (`deploy/test/deployment.yaml`) как `imagePullSecrets`.

Workflow запускается на `pull_request` и `push` в `main`. Публикация образов, подпись и деплой выполняются только для ветки `main`.