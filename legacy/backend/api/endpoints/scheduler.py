from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.post("/sync")
async def trigger_sync():
    try:
        import temporalio.client
        from backend.workflows.worker import SyncCatalogWorkflow
    except ImportError:
        raise HTTPException(status_code=503, detail="Temporal is not available")

    client = await temporalio.client.Client.connect("localhost:7233")
    handle = await client.start_workflow(
        SyncCatalogWorkflow.run,
        id="catalog-sync-workflow",
        task_queue="catalog-sync-task-queue",
    )
    return {"message": "Sync workflow triggered", "workflow_id": handle.id}
