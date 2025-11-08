import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temporalio import exceptions as temporal_exceptions

from app.temporal.client import get_temporal_client, wait_for_temporal
from app.workflows.test_workflow import TestWorkflow
from app.services.cache import connect_redis, close_redis, set_value, get_value
from app.services.nats_client import (
    NATS_SUBJECT,
    close_nats,
    connect_nats,
    clear_pending_messages,
    publish_message,
    wait_for_message,
)


app = FastAPI(title="SBS Core API", version="0.1.0")


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


@app.on_event("startup")
async def startup_event() -> None:
    await connect_nats()
    await connect_redis()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_nats()
    await close_redis()


@app.get("/")
async def root():
    return {"message": "SBS Core API", "version": "0.1.0"}


@app.post("/test-workflow", response_model=TestWorkflowResponse)
async def start_test_workflow(request: TestWorkflowRequest):
    client = None
    try:
        client = await get_temporal_client()
        
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
    except temporal_exceptions.TemporalError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Не удалось запустить workflow: {e}",
        )


@app.get("/health")
async def health():
    try:
        await wait_for_temporal()
        return {"status": "healthy", "temporal": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "temporal": f"disconnected: {e}"}


@app.post("/nats/test", response_model=NATSResponse)
async def nats_test(payload: NATSRequest):
    subject = payload.subject or NATS_SUBJECT
    try:
        clear_pending_messages()
        await publish_message(subject, payload.message.encode("utf-8"))
        data = await wait_for_message(timeout=1.0)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504, detail="Не удалось получить сообщение из NATS в течение 1 секунды"
        )
    return NATSResponse(subject=subject, received=data.decode("utf-8"))


@app.post("/redis/test", response_model=RedisResponse)
async def redis_test(payload: RedisRequest):
    await set_value(payload.key, payload.value)
    stored = await get_value(payload.key)
    return RedisResponse(key=payload.key, value=stored or "")

