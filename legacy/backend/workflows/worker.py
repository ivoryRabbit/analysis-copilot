import asyncio
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from backend.workflows.sync_catalog import sync_configs, sync_tables


@workflow.defn
class SyncCatalogWorkflow:
    @workflow.run
    async def run(self) -> None:
        configs = await sync_configs()

        for config in configs:
            print(config)
            await sync_tables(config)


async def main():
    # Start client
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue="catalog-sync-task-queue",
        workflows=[SyncCatalogWorkflow],
        activities=[],
    ):

        print("Start initial sync task")

        # While the worker is running, use the client to start the workflow.
        # Note, in many production setups, the client would be in a completely
        # separate process from the worker.
        await client.start_workflow(
            SyncCatalogWorkflow.run,
            id="catalog-sync-task-queue-id",
            task_queue="catalog-sync-task-queue",
            cron_schedule="* * * * *",
        )

        # Wait forever
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
