## SBS Platform — инфраструктурный каркас

Фреймворк для запуска ядра SBS: база данных, очереди, каркас API, мониторинг и CI/CD. Цель — чтобы команда могла поднять готовую среду декомандами и сразу приступить к разработке сервисов верхнего уровня.

---

## Быстрый старт
Локальная среда разворачивается одной командой: стэк контейнеров поднимет БД, брокеры, API, worker и наблюдаемость.

```powershell
docker-compose up -d
```

После этого:
- PostgreSQL и Alembic миграции применяются автоматически (`entrypoint.py` в контейнере API ждёт базу и запускает `alembic upgrade head`).
- Temporal Server и тестовый worker регистрируются и готовы принимать workflow.
- Redis и NATS подключаются через ленивые клиенты, API проверяет их на старте.
- OpenTelemetry, Prometheus и Grafana включаются по умолчанию; метрики доступны на `http://localhost:8000/metrics`, дашборд – `http://localhost:3000` (`admin`/`admin`).

### Проверочные вызовы
```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/version
Invoke-RestMethod http://localhost:8000/test-workflow -Method Post -Body '{"name":"Demo"}'
Invoke-RestMethod http://localhost:8000/nats/test -Method Post -Body '{"message":"ping"}'
Invoke-RestMethod http://localhost:8000/redis/test -Method Post -Body '{"key":"demo","value":"ok"}'
```

---

## Как всё устроено

### Сервисы и процессы
- **PostgreSQL 18** — основная БД платформы. Алебик инициализирует таблицу `system_settings`.
- **Temporal Server + Admin Tools** — оркестрация workflow. Worker использует очередь `test-task-queue`.
- **Redis 7** — кеш/координация. Клиент `app/services/cache.py` держит одну асинхронную сессию.
- **NATS 2.10** — шина событий. `app/services/nats_client.py` подписывает тестовый subject и даёт publish/flush.
- **SBS API** — приложение FastAPI:
  - `/health` проверяет Temporal, NATS, Redis и делает `SELECT 1`.
  - `/version` отдаёт версию и билд (из `APP_BUILD` или Git).
  - `/settings/<key>` управляет таблицей `system_settings`.
  - `/test-workflow`, `/nats/test`, `/redis/test` демонстрируют интеграции.
  - Middleware логирует запросы и пишет метрики.
- **SBS Worker** — async worker на Temporal SDK, обрабатывает учебный workflow `TestWorkflow`.
- **Prometheus 2.52 + Grafana 10** — наблюдаемость. Скрейпинг API каждые 15 секунд, готовый дашборд `SBS Infrastructure`.

### Автоматизация миграций
`entrypoint.py` запускается внутри контейнера API перед uvicorn: ждёт доступность базы (`wait_for_database`) и выполняет `command.upgrade` Alembic. Миграции лежат в `alembic/versions/`.

### OpenTelemetry поток
`app/telemetry.py` регистрирует PrometheusMetricReader, а `configure_telemetry(app)` подключается в `app/api/main.py`. Все HTTP-запросы добавляются в счётчик и гистограмму; `/metrics` отдаёт экспозицию, которую собирает Prometheus.

### CI/CD конвейер
`.github/workflows/ci.yml`:
1. `pytest`.
2. Buildx сборка Docker-образа и push в GHCR (кроме PR).
3. SBOM через Anchore и сканирование Trivy.
4. Подписание Cosign (для push в `main`).
5. `deploy-test` — Helm деплой в тестовый кластер (`scripts/deploy_test.sh`), если заданы секреты.

---

## Структура проекта

### Корень
- `docker-compose.yml` — локальное окружение.
- `requirements.txt` — зависимости Python (API/worker).
- `entrypoint.py` — ожидание БД и миграции (используется контейнером API).
- `run_api.py`, `run_worker.py` — точки запуска в dev/CI.
- `.github/workflows/ci.yml` — pipeline CI/CD.
- `README.md` — текущий документ.

### Приложение (`app/`)
- `api/main.py` — FastAPI-приложение: эндпоинты, middleware логирования, стартап/шатунинг хуки.
- `database.py` — конфигурация SQLAlchemy engine и `SessionLocal`.
- `models/system.py` — модель `SystemSetting`.
- `services/cache.py` — Redis-клиент с ленивым подключением и вспомогательными функциями.
- `services/nats_client.py` — NATS-клиент, очередь и publish/wait утилиты.
- `temporal/client.py` — функции подключения к Temporal (ленивый singleton, ожидание).
- `temporal/worker.py` — worker, регистрирующий workflow и activity.
- `workflows/test_workflow.py` и `activities/test_activity.py` — демонстрационный сценарий.
- `telemetry.py` — настройка OpenTelemetry и запись метрик.
- `__init__.py` — хранит версию приложения.

### Миграции (`alembic/`)
- `env.py`, `script.py.mako`, `versions/...` — стандартная структура Alembic.
- `20251107000000_initial.py` — создаёт `system_settings`.

### Инфраструктура (`deploy/`, `infrastructure/`, `monitoring/`, `scripts/`)
- `deploy/helm/sbs` — основной Helm-чарт (API, worker) и вложенные чарты (`charts/postgresql`, `charts/temporal`, `charts/redis`, `charts/nats`). `values.yaml` задаёт образы и параметры.
- `scripts/start_api.sh`, `scripts/start_worker.sh` — entrypoint-скрипты внутри контейнеров.
- `scripts/deploy_test.sh` — Helm деплой для CI (принимает ссылку на образ).
- `monitoring/prometheus/prometheus.yml` — scrape-конфигурация.
- `monitoring/grafana/...` — провиженинг datasources и дашборда.
- `infrastructure/terraform` — модули `network`, `kubernetes_cluster`, `virtual_machine` и окружение `environments/test`.
- `infrastructure/ansible` — роли (`common`, `docker`, `postgresql`, `temporal`, `redis`, `nats`, `sbs_api`) и playbook `site.yml`.

### Тесты
- `tests/test_sanity.py` — минимальный sanity-тест (расширяется при развитии функциональности).

---

## Переменные окружения
Все контейнеры используют значения по умолчанию, поэтому для локальных запусков ничего настраивать не требуется. При необходимости можно переопределить:

| Переменная | Назначение | Значение по умолчанию |
| --- | --- | --- |
| `DATABASE_URL` или `DATABASE_*` | Подключение к PostgreSQL | `postgresql+psycopg://postgres:secret@db:5432/app_db` |
| `TEMPORAL_HOST` / `PORT` / `NAMESPACE` | Temporal SDK | `temporal:7233`, `default` |
| `REDIS_URL` | Redis | `redis://redis:6379/0` |
| `NATS_URL` / `NATS_SUBJECT` | NATS | `nats://nats:4222`, `backup.test` |
| `APP_BUILD` | Строка build-id | вычисляется из Git |
| `OTEL_SERVICE_NAME` | Имя сервиса в метриках | `sbs-api` |

---

## CI/CD и окружения

### GitHub Actions
- **build-scan**:
  - checkout → установка Python 3.12 → `pip install -r requirements.txt`
  - `pytest`
  - `docker/build-push-action` (push, если событие не PR)
  - `anchore/sbom-action` → `actions/upload-artifact`
  - `aquasecurity/trivy-action` (фейлит job при найденных уязвимостях)
  - `cosign sign` и выгрузка `.sig/.att` (для ветки `main`)
- **deploy-test**:
  - `scripts/deploy_test.sh <IMAGE_REF>`
  - `helm dependency build` и `helm upgrade --install`


### Helm/Terraform/Ansible
Для окружений за пределами docker-compose:
- Helm-чарт служит эталонной спецификацией Kubernetes.
- Terraform описывает сетевую инфраструктуру, EKS и вспомогательные ВМ.
- Ansible автоматизирует bare-metal поставку: установка Docker и развёртывание контейнеров из образов.

---

## Диагностика и DoD
| Действие | Ожидаемый результат |
| --- | --- |
| `Invoke-RestMethod http://localhost:8000/health` | `{"status":"healthy"}` |
| `Invoke-RestMethod http://localhost:8000/version` | JSON с `version` и `build` |
| `Invoke-RestMethod http://localhost:8000/test-workflow` | Возвращает `workflow_id` и `run_id`, в Temporal admin-tools видна завершённая задача |
| `Invoke-RestMethod http://localhost:8000/nats/test` | Получаем эхо-сообщение |
| `Invoke-RestMethod http://localhost:8000/redis/test` | Возвращает записанное значение |
| `Invoke-RestMethod http://localhost:8000/settings/core.version` | Запись из таблицы `system_settings` |
| `Invoke-RestMethod http://localhost:8000/metrics` | Prometheus-совместные метрики |
| Grafana → `SBS Infrastructure` | Графики RPS, latency, 5xx, нагрузка |

---


С текущим состоянием кодовая база готова к финальному прогону CI/CD и выкладке в тестовый или продуктивный кластер. Одной командой `docker-compose up -d` вы получаете полностью рабочий контур для разработки и демонстрации. 

