from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temporalio import exceptions as temporal_exceptions

from app.temporal.client import get_temporal_client, wait_for_temporal
from app.workflows.test_workflow import TestWorkflow


app = FastAPI(title="SBS Core API", version="0.1.0")


class TestWorkflowRequest(BaseModel):
    name: str = "TestUser"


class TestWorkflowResponse(BaseModel):
    run_id: str
    workflow_id: str
    message: str


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

