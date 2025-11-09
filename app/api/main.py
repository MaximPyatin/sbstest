import asyncio
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from temporalio import exceptions as temporal_exceptions

from app import __version__ as APP_VERSION
from app.database import SessionLocal, get_db
from app.models import SystemSetting
from app.telemetry import configure_telemetry, record_http_request_metrics
from app.temporal.client import (
    close_temporal_client,
    get_temporal_client,
    wait_for_temporal,
)
from app.workflows.test_workflow import TestWorkflow
from app.services.cache import close_redis, get_redis, set_value, get_value
from app.services.nats_client import (
    NATS_SUBJECT,
    close_nats,
    clear_pending_messages,
    get_nats,
    publish_message,
    wait_for_message,
)

APP_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("sbs.api")

app = FastAPI(title="SBS Core API", version=APP_VERSION)

configure_telemetry(app)


class TestWorkflowRequest(BaseModel):
    name: str = "TestUser"


class TestWorkflowResponse(BaseModel):
    run_id: str
    workflow_id: str
    message: str


class NATSRequest(BaseModel):
    message: str = "data"
    subject: str | None = None


class NATSResponse(BaseModel):
    subject: str
    received: str


class RedisRequest(BaseModel):
    key: str
    value: str


class RedisResponse(BaseModel):
    key: str
    value: str


class SystemSettingResponse(BaseModel):
    key: str
    value: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class SystemSettingPayload(BaseModel):
    value: str | None = None
    description: str | None = None

def _resolve_build() -> str:
    """Пытаемся честно узнать номер сборки: сначала смотрим переменную, потом git."""
    env_build = os.getenv("APP_BUILD")
    if env_build:
        return env_build
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(APP_ROOT.parent),
        )
        return output.decode("utf-8").strip()
    except (subprocess.CalledProcessError, FileNotFoundError, NotADirectoryError):
        return "unknown"


def _ensure_core_version_setting() -> None:
    """Гарантируем, что в базе лежит актуальная версия ядра — пригодится для проверок здоровья."""
    with SessionLocal() as session:
        result = session.execute(
            select(SystemSetting).where(SystemSetting.key == "core.version")
        ).scalar_one_or_none()
        if result is None:
            session.add(
                SystemSetting(
                    key="core.version",
                    value=APP_VERSION,
                    description="Текущая версия ядра платформы.",
                )
            )
            session.commit()
            return

        if result.value != APP_VERSION:
            result.value = APP_VERSION
            session.commit()


@lru_cache(maxsize=1)
def get_build_metadata() -> dict[str, Any]:
    """Кешируем версию и build, чтобы не гонять git команду на каждый запрос."""
    return {
        "version": APP_VERSION,
        "build": _resolve_build(),
    }


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Логируем каждый запрос по-человечески: с request_id, статусом и временем выполнения."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    start_time = time.perf_counter()

    logger.info(
        "request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    duration_seconds: float

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000
        duration_seconds = duration_ms / 1000
        logger.exception(
            "request_id=%s method=%s path=%s status=error duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        record_http_request_metrics(request, 500, duration_seconds)
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    duration_seconds = duration_ms / 1000
    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    record_http_request_metrics(request, response.status_code, duration_seconds)
    response.headers["X-Request-ID"] = request_id
    return response


@app.on_event("startup")
async def startup_event() -> None:
    """На старте убеждаемся, что Temporal, NATS, Redis и версия в БД готовы к работе."""
    await wait_for_temporal()
    await get_nats()
    await get_redis()
    await asyncio.to_thread(_ensure_core_version_setting)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """При выключении сервиса аккуратно закрываем все подключения, чтобы ничего не висело."""
    await close_nats()
    await close_redis()
    await close_temporal_client()


@app.get("/")
async def root():
    """Отвечаем, что сервис жив, и делимся номером версии со сборкой."""
    metadata = get_build_metadata()
    return {"message": "SBS Core API", **metadata}


@app.get("/health")
async def health(
    _: Any = Depends(get_temporal_client),
    __: Any = Depends(get_nats),
    ___: Any = Depends(get_redis),
    db: Session = Depends(get_db),
):
    """Пинг-понг для операторов: проверяем Temporal, NATS, Redis и делаем SELECT 1."""
    db.execute(text("SELECT 1"))
    return {"status": "healthy"}


@app.get("/version")
async def version():
    """Возвращаем компактный JSON с версией и build, чтобы проверяющие не лезли в git."""
    return get_build_metadata()


@app.post("/test-workflow", response_model=TestWorkflowResponse)
async def start_test_workflow(
    request: TestWorkflowRequest,
    client=Depends(get_temporal_client),
):
    """Стартуем учебный workflow в Temporal и отдаём id, чтобы легко проверить связность."""
    try:
        handle = await client.start_workflow(
            TestWorkflow.run,
            request.name,
            id=f"test-workflow-{request.name}",
            task_queue="test-task-queue",
        )
        return TestWorkflowResponse(
            run_id=handle.result_run_id,
            workflow_id=handle.id,
            message=f"Workflow запущен для {request.name}",
        )
    except temporal_exceptions.TemporalError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Не удалось запустить workflow: {exc}",
        ) from exc


@app.post("/nats/test", response_model=NATSResponse)
async def nats_test(payload: NATSRequest, _: Any = Depends(get_nats)):
    """Публикуем сообщение в NATS, ждём отклика и возвращаем, что реально получили."""
    subject = payload.subject or NATS_SUBJECT
    try:
        clear_pending_messages()
        await publish_message(subject, payload.message.encode("utf-8"))
        data = await wait_for_message(timeout=1.0)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Не удалось получить сообщение из NATS в течение 1 секунды",
        ) from None
    return NATSResponse(subject=subject, received=data.decode("utf-8"))


@app.post("/redis/test", response_model=RedisResponse)
async def redis_test(payload: RedisRequest, _: Any = Depends(get_redis)):
    """Сохраняем пару ключ-значение в Redis и тут же читаем обратно для проверки."""
    await set_value(payload.key, payload.value)
    stored = await get_value(payload.key)
    return RedisResponse(key=payload.key, value=stored or "")


@app.get("/settings/{key}", response_model=SystemSettingResponse)
async def get_setting(key: str, db: Session = Depends(get_db)):
    """Достаём запись настройки по ключу; если её нет — честно говорим 404."""
    setting = (
        db.execute(select(SystemSetting).where(SystemSetting.key == key))
        .scalars()
        .first()
    )
    if setting is None:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return setting


@app.put("/settings/{key}", response_model=SystemSettingResponse)
async def upsert_setting(
    key: str,
    payload: SystemSettingPayload,
    db: Session = Depends(get_db),
):
    """Создаём или обновляем инфраструктурную настройку; пригодится DevOps-скриптам."""
    statement = select(SystemSetting).where(SystemSetting.key == key)
    setting = db.execute(statement).scalars().first()

    if setting is None:
        setting = SystemSetting(
            key=key,
            value=payload.value,
            description=payload.description,
        )
        db.add(setting)
    else:
        setting.value = payload.value
        setting.description = payload.description

    db.commit()
    db.refresh(setting)
    return setting

